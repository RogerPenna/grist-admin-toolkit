import streamlit as st
import pandas as pd
import requests
import os
import time
import json
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from dotenv import load_dotenv

# Page Configuration
st.set_page_config(
    page_title="Gestor PQC - Grist",
    page_icon="📊",
    layout="wide"
)

# 1. Configuration & Setup
load_dotenv()
API_KEY = os.getenv("GRIST_API_KEY")
GENERIC_BASE_URL = "https://docs.getgrist.com/api"

if not API_KEY:
    st.error("❌ GRIST_API_KEY não encontrada no arquivo .env")
    st.stop()

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest"
}

# Helper: Email Normalization
def normalize_email(email_str):
    if not email_str: return ""
    # 1. Strip and Lowercase
    email_str = email_str.strip().lower()
    # 2. Normalize to NFKD (separates base characters from accents)
    nks = unicodedata.normalize('NFKD', email_str)
    # 3. Keep only base characters (removes combining marks like accents/cedillas)
    # Also handle some manual replacements if needed, but NFKD covers most.
    sanitized = "".join([c for c in nks if not unicodedata.combining(c)])
    # 4. Remove any non-standard characters just in case
    sanitized = re.sub(r'[^a-z0-9@._\-\+]', '', sanitized)
    return sanitized

# 2. API Helper Functions with Caching

@st.cache_data(ttl=300)
def get_orgs():
    """Fetches available organizations."""
    try:
        response = requests.get(f"{GENERIC_BASE_URL}/orgs", headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro ao buscar organizações: {e}")
        return []

@st.cache_data(ttl=300)
def get_org_users(base_url, org_id):
    """Fetches users at the organization level."""
    try:
        url = f"{base_url}/orgs/{org_id}/access"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        return data.get("users", [])
    except Exception as e:
        st.error(f"Erro ao buscar usuários da organização: {e}")
        return []

@st.cache_data(ttl=300)
def get_workspaces_and_docs(base_url, org_id):
    """Fetches all workspaces and their documents for an org."""
    try:
        url = f"{base_url}/orgs/{org_id}/workspaces"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro ao buscar workspaces: {e}")
        return []

@st.cache_data(ttl=600)
def get_doc_users(base_url, doc_id):
    """Fetches users assigned to a specific document."""
    try:
        url = f"{base_url}/docs/{doc_id}/access"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        return data.get("users", [])
    except Exception as e:
        return []

def update_doc_access(base_url, doc_id, email, role):
    """Updates user access via PATCH /access with delta."""
    try:
        url = f"{base_url}/docs/{doc_id.strip()}/access"
        payload = {"delta": {"users": {email.strip(): role}}}
        response = requests.patch(url, headers=HEADERS, json=payload)
        if response.status_code != 200:
             return False, f"Erro {response.status_code}: {response.text}"
        return True, "Sucesso!"
    except Exception as e:
        return False, str(e)

@st.cache_data(ttl=300)
def get_tables(base_url, doc_id):
    """Fetches list of tables for a document."""
    try:
        url = f"{base_url}/docs/{doc_id}/tables"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json().get('tables', [])
    except Exception as e:
        st.error(f"Erro ao buscar tabelas: {e}")
        return []

def get_tables_no_cache(base_url, doc_id):
    """Fetches list of tables for a document without caching."""
    try:
        url = f"{base_url}/docs/{doc_id}/tables"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json().get('tables', [])
    except Exception as e:
        return []

@st.cache_data(ttl=300)
def get_doc_usage(base_url, doc_id):
    """Fetches usage statistics for a document. Returns (data, status_code)."""
    try:
        url = f"{base_url}/docs/{doc_id}/usage"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json(), 200
        return None, response.status_code
    except Exception:
        return None, 500

@st.cache_data(ttl=300)
def get_org_usage(base_url, org_id):
    """Fetches usage for all documents in an organization in a single call."""
    try:
        url = f"{base_url}/orgs/{org_id}/usage"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

@st.cache_data(ttl=300)
def get_table_row_count(base_url, doc_id, table_id):
    """Fetches row count for a specific table using SQL API."""
    try:
        # Use SQL for efficiency if possible
        url = f"{base_url}/docs/{doc_id}/sql?q=SELECT COUNT(*) as count FROM {table_id}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            records = response.json().get('records', [])
            if records:
                return records[0].get('fields', {}).get('count', 0)
        
        # Fallback to records endpoint with limit=1 to check if table is empty or not
        # Note: Grist API doesn't return total count easily in /records unless you fetch all.
        # But SQL API should work on most documents if we have access.
        return 0
    except Exception:
        return 0

@st.cache_data(ttl=300)
def get_doc_attachments_info(base_url, doc_id):
    """Fetches all attachments metadata for a document."""
    try:
        url = f"{base_url}/docs/{doc_id}/attachments"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            # Grist returns {"records": [...]} or sometimes just a list depending on version
            if isinstance(data, dict) and 'records' in data:
                return data['records']
            elif isinstance(data, list):
                return data
        return []
    except Exception:
        return []

@st.cache_data(ttl=300)
def get_table_columns_count(base_url, doc_id, table_id):
    """Returns number of columns in a table."""
    try:
        cols = get_columns(base_url, doc_id, table_id)
        return len(cols)
    except:
        return 0

def get_columns_no_cache(base_url, doc_id, table_id):
    """Fetches columns for a specific table without caching."""
    try:
        url = f"{base_url}/docs/{doc_id}/tables/{table_id}/columns"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json().get('columns', [])
    except Exception as e:
        return []

@st.cache_data(ttl=300)
def get_columns(base_url, doc_id, table_id):
    """Fetches columns for a specific table."""
    try:
        url = f"{base_url}/docs/{doc_id}/tables/{table_id}/columns"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json().get('columns', [])
    except Exception as e:
        st.error(f"Erro ao buscar colunas: {e}")
        return []

def add_table_record(base_url, doc_id, table_id, col_id, value):
    """Adds a new record to a table with a specific value in one column."""
    try:
        url = f"{base_url}/docs/{doc_id}/tables/{table_id}/records"
        payload = {
            "records": [{"fields": {col_id: value}}]
        }
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        return True, "Registro adicionado com sucesso!"
    except Exception as e:
        return False, str(e)

def add_records(base_url, doc_id, table_id, records):
    """Adds multiple records to a table."""
    try:
        url = f"{base_url}/docs/{doc_id}/tables/{table_id}/records"
        # records should be a list of dictionaries: [{"Nome": "João", "Idade": 30}, ...]
        payload = {"records": [{"fields": r} for r in records]}
        response = requests.post(url, headers=HEADERS, json=payload)
        if response.status_code == 200:
            return True, f"{len(records)} registros adicionados."
        return False, f"Erro {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def create_table(base_url, doc_id, table_id, columns_payload):
    """Creates a new table in the document with the provided columns."""
    try:
        url = f"{base_url}/docs/{doc_id}/tables"
        # Grist requires columns to be present when creating a table
        payload = {"tables": [{"id": table_id, "columns": columns_payload}]}
        response = requests.post(url, headers=HEADERS, json=payload)
        if response.status_code == 200:
            return True, "Tabela e colunas criadas com sucesso!"
        # If table already exists, return a specific status
        if "already exists" in response.text.lower():
            return False, "EXISTING"
        return False, f"Erro {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def add_columns(base_url, doc_id, table_id, columns_payload):
    """Adds columns to an existing table."""
    try:
        url = f"{base_url}/docs/{doc_id}/tables/{table_id}/columns"
        # columns_payload should be a list of {id, fields: {label, type, formula, isFormula, ...}}
        payload = {"columns": columns_payload}
        response = requests.post(url, headers=HEADERS, json=payload)
        if response.status_code == 200:
            return True, "Colunas adicionadas com sucesso!"
        return False, f"Erro {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def delete_tables_batch(base_url, doc_id, table_ids):
    """Deletes multiple tables in a single transaction using the /apply endpoint."""
    if not table_ids:
        return True, "Nenhuma tabela para remover."
    try:
        url = f"{base_url}/docs/{doc_id}/apply"
        # Grist structural action: ["RemoveTable", tableId]
        # The /apply endpoint expects a bare array of actions: [ [action1], [action2] ]
        payload = [["RemoveTable", t_id] for t_id in table_ids]
        response = requests.post(url, headers=HEADERS, json=payload)
        if response.status_code == 200:
            return True, f"{len(table_ids)} tabelas removidas com sucesso."
        return False, f"Erro {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def create_document(base_url, workspace_id, doc_name):
    """Creates a new Grist document in a specific workspace."""
    try:
        url = f"{base_url}/workspaces/{workspace_id}/docs"
        payload = {"name": doc_name}
        response = requests.post(url, headers=HEADERS, json=payload)
        if response.status_code == 200:
            return True, response.json() # Returns the new doc ID string
        return False, f"Erro {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def load_audit_configs():
    """Loads saved audit configurations from JSON."""
    if os.path.exists("audit_configs.json"):
        try:
            with open("audit_configs.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_audit_config(name, config_data):
    """Saves a new audit configuration."""
    configs = load_audit_configs()
    configs[name] = config_data
    with open("audit_configs.json", "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=2, ensure_ascii=False)

# --- ACL HELPER FUNCTIONS ---

def fetch_table_records(base_url, doc_id, table_name):
    """Fetches all records from a table."""
    try:
        url = f"{base_url}/docs/{doc_id}/tables/{table_name}/records"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 404:
            return [] # Table usually doesn't exist if no rules
        if response.status_code == 403:
            raise PermissionError("Acesso negado. É necessário ser OWNER do documento para ler metadados de regras.")
        response.raise_for_status()
        return response.json().get('records', [])
    except PermissionError as pe:
        raise pe
    except Exception:
        return []

def get_denormalized_rules(base_url, doc_id):
    """Fetches _grist_ACLRules and _grist_ACLResources and merges them."""
    try:
        rules_records = fetch_table_records(base_url, doc_id, '_grist_ACLRules')
        resources_records = fetch_table_records(base_url, doc_id, '_grist_ACLResources')
    except PermissionError as e:
        st.error(f"🚫 {e}")
        return []

    if not rules_records:
        return []

    # Map resource ID to object (tableId, colIds)
    # Resource fields: tableId, colIds
    res_map = {}
    for r in resources_records:
        rid = r['id']
        rf = r['fields']
        tid = rf.get('tableId') or "*"
        cids = rf.get('colIds') or "*"
        res_map[rid] = f"{tid} [{cids}]" if cids != "*" else tid
    
    denormalized = []
    for rule in rules_records:
        fields = rule['fields']
        res_id = fields.get('resource')
        
        # Resolve resource name
        resource_name = res_map.get(res_id, "Geral/Desconhecido")
        
        # Build display dict
        # Columns requested: Recurso, Condição, Permissões
        denormalized.append({
            "ID Regra": rule['id'],
            "Recurso": resource_name,
            "Condição": fields.get('aclFormula') or "(Sempre)",
            "Permissões": fields.get('permissionsText'),
            "Memo": fields.get('memo') or "",
            "Posição": fields.get('rulePos')
        })
    
    # Sort by rulePos
    denormalized.sort(key=lambda x: x.get('Posição', 0))
    return denormalized

# 3. Main UI Layout

st.title("🏆 Gestor de Acessos PQC-RS (Grist)")

# --- Sidebar: Org Selection ---
st.sidebar.header("Configuração")
orgs = get_orgs()

if not orgs:
    st.warning("Nenhuma organização encontrada.")
    st.stop()

org_map = {f"{org['name']} ({org['id']})": org['id'] for org in orgs}
org_domain_map = {org['id']: org.get('domain') for org in orgs}

# Try to default to PQC
default_idx = 0
keys_list = list(org_map.keys())
for i, name_with_id in enumerate(keys_list):
    if "Qualidade Contábil" in name_with_id:
        default_idx = i
        break

selected_org_key = st.sidebar.selectbox(
    "Selecione a Organização", 
    keys_list, 
    index=default_idx, 
    key="org_selector_main"
)
selected_org_id = org_map[selected_org_key]
selected_org_name = selected_org_key # For display purposes
selected_domain = org_domain_map.get(selected_org_id)

# Garante inicialização do mapped_data
if "mapped_data" not in st.session_state:
    st.session_state.mapped_data = None

# Definição da URL Base Dinâmica
# Personal orgs often return a shard domain (e.g. docs-26) which might not have the API endpoint active or requires auth tweaks.
# It is safer to use the generic docs.getgrist.com for Personal.
is_personal = "personal" in selected_org_name.lower()

if selected_domain and not is_personal:
    CURRENT_BASE_URL = f"https://{selected_domain}.getgrist.com/api"
else:
    CURRENT_BASE_URL = GENERIC_BASE_URL

st.sidebar.caption(f"📍 Base URL: {CURRENT_BASE_URL}")

if st.sidebar.button("🔄 Forçar Recarga Geral", key="force_reload_btn"):
    st.cache_data.clear()
    st.session_state.mapped_data = None
    st.rerun()

# Main Content Tabs
tabs_list = ["👥 Visão Global (Org)", "🗺️ Mapeamento de Documentos", "⚡ Ações Rápidas", "🛡️ Auditoria de Regras", "❓ Ajuda", "⚖️ Auditoria de Integridade", "🏗️ Clonador de Templates", "🛠️ Blueprint (Novo Doc)", "📊 Limites e Uso", "📥 Popular Tabelas"]

# Para garantir a persistência em versões que não aceitam 'key' no st.tabs,
# mantemos o componente, mas evitamos chamadas de rerun que não sejam estritamente necessárias.
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(tabs_list)

# --- TAB 1: Global Organization Users ---
with tab1:
    st.header(f"Usuários: {selected_org_name}")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        f_name = st.text_input("Filtrar por Nome", key="search_g_name")
    with col_g2:
        f_email = st.text_input("Filtrar por Email", key="search_g_email")

    users = get_org_users(CURRENT_BASE_URL, selected_org_id)
    
    if users:
        df_users = pd.DataFrame(users)
        df_display = df_users.rename(columns={'email': 'Email', 'name': 'Nome', 'access': 'Acesso Global'})
        df_display = df_display[['Email', 'Nome', 'Acesso Global']]
        
        if f_name:
            df_display = df_display[df_display['Nome'].str.contains(f_name, case=False, na=False, regex=False)]
        if f_email:
            df_display = df_display[df_display['Email'].str.contains(f_email, case=False, na=False, regex=False)]
            
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # --- NEW: User Document Details (Cross-reference with Tab 2) ---
        st.divider()
        st.subheader("🕵️ Detalhes de Acesso por Usuário")
        
        if st.session_state.mapped_data is not None:
            # Use filtered emails from the main table
            valid_emails = sorted([e for e in df_display['Email'].unique() if e and e != '-'])
            
            selected_user_detail = st.selectbox("Selecione um Usuário (da lista acima) para ver seus Documentos:", valid_emails, key="sel_user_detail")
            
            if selected_user_detail:
                # Filter mapped data
                user_docs = st.session_state.mapped_data[st.session_state.mapped_data['Email'] == selected_user_detail]
                # Hide inherited access (requested by user)
                user_docs = user_docs[~user_docs['Nível de Acesso'].str.contains("Herdado", case=False, na=False)]
                
                if not user_docs.empty:
                    st.write(f"📂 **Documentos com acesso explícito para: {selected_user_detail}**")
                    st.dataframe(
                        user_docs[['Documento', 'Workspace', 'Nível de Acesso']], 
                        use_container_width=True, 
                        hide_index=True
                    )
                else:
                    st.warning(f"O usuário {selected_user_detail} não possui acessos diretos em documentos (apenas herdados ou nenhum).")
        else:
            st.info("💡 Para ver a lista de documentos de cada usuário aqui, vá até a aba **'🗺️ Mapeamento de Documentos'** e clique em **'Iniciar Mapeamento Completo'**.")

        # --- NEW SECTION: MASS VERIFICATION ---
        st.divider()
        st.subheader("🔍 Verificação em Massa (Team Site)")
        st.markdown("Cole uma lista de emails para verificar se já estão na organização e em quais documentos.")
        
        emails_raw = st.text_area("Emails para Verificar", placeholder="usuario1@email.com, usuario2@email.com...", help="Aceita emails separados por vírgula, espaço ou linha.", key="mass_check_input")
        
        if emails_raw:
            # 1. Process and Sanitize
            raw_list = [e.strip() for e in re.split(r'[,\s\n]+', emails_raw) if e.strip()]
            sanitized_map = {e: normalize_email(e) for e in raw_list}
            unique_sanitized = sorted(list(set(sanitized_map.values())))
            
            # 2. Build Comparison Data
            org_emails = set(df_users['email'].str.lower().str.strip().unique()) if 'email' in df_users.columns else set()
            
            check_data = []
            for sem in unique_sanitized:
                # In Org?
                in_org = "✅ Sim" if sem in org_emails else "❌ Não"
                
                # Documents?
                docs_found = []
                if st.session_state.mapped_data is not None:
                    user_docs = st.session_state.mapped_data[st.session_state.mapped_data['Email'].str.lower() == sem]
                    # Filter out inherited
                    user_docs = user_docs[~user_docs['Nível de Acesso'].str.contains("Herdado", case=False, na=False)]
                    docs_found = user_docs['Documento'].unique().tolist()
                
                check_data.append({
                    "Selecionar": False,
                    "Email Sanitizado": sem,
                    "No Team Site?": in_org,
                    "Documentos Atuais": ", ".join(docs_found) if docs_found else "—"
                })
            
            df_check = pd.DataFrame(check_data)
            # Order by "No Team Site?" (No first)
            df_check = df_check.sort_values(by="No Team Site?", ascending=True)
            
            st.write(f"📋 **{len(unique_sanitized)} emails únicos processados.**")
            
            # 3. Display with Selection
            edited_check = st.data_editor(
                df_check,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Selecionar": st.column_config.CheckboxColumn("Sel", default=False),
                    "Email Sanitizado": st.column_config.TextColumn("Email Sanitizado", width="medium"),
                    "No Team Site?": st.column_config.TextColumn("No Team Site?", width="small"),
                    "Documentos Atuais": st.column_config.TextColumn("Documentos Atuais", width="large"),
                },
                key="mass_check_editor"
            )
            
            # 4. Bulk Action: Add to Document
            sel_to_add = edited_check[edited_check["Selecionar"]]
            
            if not sel_to_add.empty:
                st.info(f"👉 **{len(sel_to_add)} emails selecionados.**")
                
                # Choose target document
                if st.session_state.mapped_data is not None:
                    all_docs_list = st.session_state.mapped_data[['Documento', 'Doc ID']].drop_duplicates()
                    doc_opts_mass = {r['Documento']: r['Doc ID'] for _, r in all_docs_list.iterrows()}
                    
                    c_m1, c_m2, c_m3 = st.columns([2, 1, 1])
                    target_m = c_m1.selectbox("Selecione o Documento para incluir:", sorted(doc_opts_mass.keys()), index=None, placeholder="Buscar doc...", key="mass_add_doc_sel")
                    lvl_m = c_m2.selectbox("Nível", ["viewers", "editors", "owners"], key="mass_add_lvl_sel")
                    
                    if c_m3.button("➕ Incluir em Bloco", type="primary", key="mass_add_btn"):
                        if not target_m:
                            st.error("Selecione um documento!")
                        else:
                            tid_m = doc_opts_mass[target_m]
                            success_m = 0
                            errors_m = []
                            with st.status(f"Adicionando ao documento '{target_m}'...", expanded=True) as status:
                                for _, row in sel_to_add.iterrows():
                                    target_em = row["Email Sanitizado"]
                                    s, m = update_doc_access(CURRENT_BASE_URL, tid_m, target_em, lvl_m)
                                    if s:
                                        success_m += 1
                                        st.write(f"✅ {target_em}: OK")
                                    else:
                                        errors_m.append(f"{target_em}: {m}")
                                        st.write(f"❌ {target_em}: {m}")
                                status.update(label="Concluído!", state="complete")
                            
                            if success_m: st.toast(f"{success_m} usuários adicionados!")
                            if errors_m: st.error(f"Erros: {len(errors_m)}")
                            time.sleep(1); st.cache_data.clear(); st.rerun()
                else:
                    st.warning("⚠️ Mapeamento de documentos necessário para esta ação. Vá à aba 🗺️ Mapeamento.")
            
    else:
        st.info("Nenhum usuário encontrado.")

# --- TAB 2: Document Mapping ---
with tab2:
    st.header("Mapeamento de Documentos")
    
    # LOAD CACHED MAPPING ON STARTUP
    MAPPING_FILE = "mapping_cache.json"
    
    if st.session_state.mapped_data is None:
        if os.path.exists(MAPPING_FILE):
            try:
                with open(MAPPING_FILE, "r", encoding="utf-8") as f:
                    cache_obj = json.load(f)
                    # Check if org matches
                    if cache_obj.get("org_id") == selected_org_id:
                        st.session_state.mapped_data = pd.DataFrame(cache_obj["data"])
                        st.session_state.mapping_ts = cache_obj.get("timestamp", "")
            except Exception:
                pass # Ignore load errors

    # Display Timestamp
    if 'mapping_ts' in st.session_state and st.session_state.mapping_ts:
        st.caption(f"📅 Última atualização: {st.session_state.mapping_ts}")
    else:
        st.caption("⚠️ Nenhum mapeamento recente encontrado.")

    if st.button("🚀 Iniciar/Atualizar Mapeamento", key="start_map_btn"):
        with st.status("Varrendo documentos...", expanded=True) as status:
            workspaces = get_workspaces_and_docs(CURRENT_BASE_URL, selected_org_id)
            all_docs = []
            for ws in workspaces:
                for doc in ws.get('docs', []):
                    all_docs.append({'id': doc['id'], 'name': doc['name'], 'ws': ws.get('name')})
            
            consolidated = []
            progress = st.progress(0)
            for i, doc in enumerate(all_docs):
                doc_users = get_doc_users(CURRENT_BASE_URL, doc['id'])
                d_name = doc['name'].strip()
                if doc_users:
                    for u in doc_users:
                        acc = u.get('access') or f"{u.get('parentAccess')} (Herdado)"
                        consolidated.append({
                            'Selecionar': False,
                            'Documento': d_name,
                            'Email': (u.get('email') or "").strip(),
                            'Nome': (u.get('name') or "").strip(),
                            'Nível de Acesso': acc,
                            'Workspace': doc['ws'],
                            'Doc ID': doc['id']
                        })
                else:
                    consolidated.append({
                        'Selecionar': False, 'Documento': d_name, 'Email': '-', 'Nome': '-',
                        'Nível de Acesso': 'Indefinido', 'Workspace': doc['ws'], 'Doc ID': doc['id']
                    })
                progress.progress((i + 1) / len(all_docs))
            
            df_map = pd.DataFrame(consolidated)
            st.session_state.mapped_data = df_map
            
            # SAVE TO CACHE
            ts_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            st.session_state.mapping_ts = ts_now
            with open(MAPPING_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "org_id": selected_org_id,
                    "timestamp": ts_now,
                    "data": consolidated
                }, f, indent=2, ensure_ascii=False)
                
            status.update(label="Mapeamento concluído e salvo!", state="complete")

    if st.session_state.mapped_data is not None:
        df = st.session_state.mapped_data
        
        st.markdown("### 🔍 Filtros")
        hide_inh = st.checkbox("Ocultar herdados", value=True, key="hide_inh_chk")
        
        c1, c2, c3, c4 = st.columns(4)
        f_doc = c1.text_input("Doc", key="f_doc")
        f_em = c2.text_input("Email", key="f_em")
        f_nm = c3.text_input("Nome", key="f_nm")
        f_ac = c4.text_input("Acesso", key="f_ac")

        df_f = df.copy()
        if hide_inh:
            df_f = df_f[~df_f['Nível de Acesso'].str.contains("Herdado|Indefinido", case=False, na=False)]
        if f_doc: df_f = df_f[df_f['Documento'].str.contains(f_doc, case=False, na=False, regex=False)]
        if f_em: df_f = df_f[df_f['Email'].str.contains(f_em, case=False, na=False, regex=False)]
        if f_nm: df_f = df_f[df_f['Nome'].str.contains(f_nm, case=False, na=False, regex=False)]
        if f_ac: df_f = df_f[df_f['Nível de Acesso'].str.contains(f_ac, case=False, na=False, regex=False)]

        # --- CONTADOR E SELEÇÃO EM MASSA ---
        st.info(f"📊 Mostrando **{len(df_f)}** de **{len(df)}** registros totais.")
        
        col_sel1, col_sel2, _ = st.columns([1, 1, 2])
        if col_sel1.button("✅ Selecionar Todos Filtrados"):
            st.session_state.mapped_data.loc[df_f.index, 'Selecionar'] = True
            st.rerun()
        if col_sel2.button("❌ Desmarcar Todos"):
            st.session_state.mapped_data['Selecionar'] = False
            st.rerun()

        def style_acc(v):
            v = str(v).lower()
            if 'owner' in v: return 'background-color: #ffcccc'
            if 'editor' in v: return 'background-color: #cce5ff'
            if 'viewer' in v: return 'background-color: #e6ffcc'
            return 'color: #999'

        edited_df = st.data_editor(
            df_f.style.map(style_acc, subset=['Nível de Acesso']),
            use_container_width=True, hide_index=True,
            column_config={"Doc ID": None, "Selecionar": st.column_config.CheckboxColumn("Sel", default=False)},
            disabled=["Documento", "Email", "Nome", "Nível de Acesso", "Workspace"],
            key="editor_mapping"
        )
        
        selected = edited_df[edited_df['Selecionar']]
        
        if not selected.empty:
            st.divider()
            st.subheader(f"📦 Operações em Massa ({len(selected)} itens)")
            
            # Options
            all_docs_list = st.session_state.mapped_data[['Documento', 'Doc ID']].drop_duplicates()
            doc_opts = {r['Documento']: r['Doc ID'] for _, r in all_docs_list.iterrows()}
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                dest = st.selectbox("Documento Destino", sorted(doc_opts.keys()), index=None, placeholder="Pesquise...", key="bulk_dest")
                if st.button("📄 Copiar", key="btn_bulk_cp", disabled=not dest):
                    target_id = doc_opts[dest]
                    for _, row in selected.iterrows():
                        role = 'editors'
                        if 'owner' in row['Nível de Acesso'].lower(): role = 'owners'
                        elif 'viewer' in row['Nível de Acesso'].lower(): role = 'viewers'
                        update_doc_access(CURRENT_BASE_URL, target_id, row['Email'], role)
                    st.toast("Cópia finalizada!")
                    st.cache_data.clear(); time.sleep(1); st.rerun()

                if st.button("🚚 Mover", key="btn_bulk_mv", disabled=not dest):
                    target_id = doc_opts[dest]
                    for _, row in selected.iterrows():
                        role = 'editors'
                        if 'owner' in row['Nível de Acesso'].lower(): role = 'owners'
                        elif 'viewer' in row['Nível de Acesso'].lower(): role = 'viewers'
                        update_doc_access(CURRENT_BASE_URL, target_id, row['Email'], role)
                        update_doc_access(CURRENT_BASE_URL, row['Doc ID'], row['Email'], None)
                    st.toast("Movimentação finalizada!")
                    st.cache_data.clear(); time.sleep(1); st.rerun()

            with col_b:
                new_lvl = st.selectbox("Alterar Nível", ["viewers", "editors", "owners"], key="bulk_lvl")
                if st.button("✏️ Atualizar Selecionados", key="btn_bulk_upd"):
                    for _, row in selected.iterrows():
                        update_doc_access(CURRENT_BASE_URL, row['Doc ID'], row['Email'], new_lvl)
                    st.toast("Nível atualizado!")
                    st.cache_data.clear(); time.sleep(1); st.rerun()
                
                if st.button("🗑️ Remover Selecionados", key="btn_bulk_rm", type="primary"):
                    for _, row in selected.iterrows():
                        update_doc_access(CURRENT_BASE_URL, row['Doc ID'], row['Email'], None)
                    st.toast("Removidos com sucesso!")
                    st.cache_data.clear(); time.sleep(1); st.rerun()

# --- TAB 3: Quick Actions ---
with tab3:
    st.header("⚡ Ações Rápidas")
    if st.session_state.mapped_data is not None:
        all_docs_q = st.session_state.mapped_data[['Documento', 'Doc ID']].drop_duplicates()
        doc_opts_q = {r['Documento']: r['Doc ID'] for _, r in all_docs_q.iterrows()}
        target_q = st.selectbox("Selecionar Documento", sorted(doc_opts_q.keys()), index=None, placeholder="Buscar...", key="q_doc_sel")
        
        if target_q:
            tid = doc_opts_q[target_q]
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🟢 Adicionar (Massa)")
                ems_raw = st.text_area("Email(s)", help="Cole um ou mais emails separados por vírgula, espaço ou linha.", key="q_add_ems")
                rl = st.selectbox("Nível", ["viewers", "editors", "owners"], key="q_add_rl")
                if st.button("Adicionar em Massa", key="q_add_btn"):
                    # Process emails
                    # Split by comma, space, or newline
                    emails = [e.strip().lower() for e in re.split(r'[,\s\n]+', ems_raw) if e.strip()]
                    
                    if not emails:
                        st.error("Nenhum email válido inserido.")
                    else:
                        success_count = 0
                        errors = []
                        with st.status(f"Adicionando {len(emails)} usuários...", expanded=True) as status:
                            for em in emails:
                                s, m = update_doc_access(CURRENT_BASE_URL, tid, em, rl)
                                if s:
                                    success_count += 1
                                    st.write(f"✅ {em}: Sucesso")
                                else:
                                    errors.append(f"{em}: {m}")
                                    st.write(f"❌ {em}: {m}")
                            status.update(label="Processamento concluído!", state="complete")
                        
                        if success_count > 0:
                            st.toast(f"{success_count} usuários adicionados!")
                        if errors:
                            st.error(f"Ocorreram {len(errors)} erros.")
                        
                        st.cache_data.clear(); time.sleep(1); st.rerun()
            with c2:
                st.subheader("🔴 Remover (Massa)")
                em_r_raw = st.text_area("Email(s)", help="Cole um ou mais emails para remover.", key="q_rm_ems")
                if st.button("Remover em Massa", key="q_rm_btn", type="primary"):
                    emails_r = [e.strip().lower() for e in re.split(r'[,\s\n]+', em_r_raw) if e.strip()]
                    
                    if not emails_r:
                        st.error("Nenhum email válido inserido.")
                    else:
                        success_count = 0
                        errors = []
                        with st.status(f"Removendo {len(emails_r)} usuários...", expanded=True) as status:
                            for em in emails_r:
                                s, m = update_doc_access(CURRENT_BASE_URL, tid, em, None)
                                if s:
                                    success_count += 1
                                    st.write(f"✅ {em}: Removido")
                                else:
                                    errors.append(f"{em}: {m}")
                                    st.write(f"❌ {em}: {m}")
                            status.update(label="Remoção concluída!", state="complete")
                        
                        if success_count > 0:
                            st.toast(f"{success_count} usuários removidos!")
                        if errors:
                            st.error(f"Ocorreram {len(errors)} erros.")
                            
                        st.cache_data.clear(); time.sleep(1); st.rerun()
    else:
        st.info("Faça o mapeamento na aba anterior primeiro.")

# --- TAB 4: Rules Audit ---
import os
from datetime import datetime

# ... existing code ...

def backup_rules_locally(doc_name, rules_data):
    """Saves rules to backups/ folder."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = doc_name.replace(" ", "_")
        filename = f"backups/rules_{safe_name}_{timestamp}.json"
        
        import json
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(rules_data, f, indent=2, ensure_ascii=False)
        return True, filename
    except Exception as e:
        return False, str(e)

def find_or_create_resource(base_url, doc_id, resource_str):
    """
    Parses resource string "Table [Cols]" -> finds/creates ID in _grist_ACLResources.
    """
    # Parse string
    import re
    table_id = "*"
    col_ids = "*"
    
    # Format: "Table" or "Table [Col1, Col2]"
    match = re.match(r"^(.*?) \[ (.*?) \]$", resource_str) # Simple regex, might need tweaking for spaces
    # Actually, let's look at how we formatted it: f"{tid} [{cids}]" if cids != "*"
    
    if "[" in resource_str and resource_str.endswith("]"):
        parts = resource_str.split(" [")
        table_id = parts[0].strip()
        col_ids = parts[1].rstrip("]").strip()
    else:
        table_id = resource_str.strip()
        col_ids = "*"
        
    # 1. Search existing
    # We need to fetch all resources again to check. Inefficient for loop, but safest.
    # Optimization: Pass a cache map if possible. For now, fetch all.
    all_res = fetch_table_records(base_url, doc_id, '_grist_ACLResources')
    for r in all_res:
        rf = r['fields']
        r_tid = rf.get('tableId') or "*"
        r_cids = rf.get('colIds') or "*"
        if r_tid == table_id and r_cids == col_ids:
            return r['id']

    # 2. Create if not found
    url = f"{base_url}/docs/{doc_id}/tables/_grist_ACLResources/records"
    payload = {
        'records': [{
            'fields': {
                'tableId': table_id,
                'colIds': col_ids
            }
        }]
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    resp.raise_for_status()
    # Returns {records: [{id: 123}]}
    return resp.json()['records'][0]['id']

def apply_denormalized_rules(base_url, doc_id, new_rules_json):
    """Renormalizes and overwrites _grist_ACLRules."""
    # 1. Delete all existing Rules
    # Fetch IDs first
    current = fetch_table_records(base_url, doc_id, '_grist_ACLRules')
    if current:
        ids_to_del = [r['id'] for r in current]
        # Chunking delete just in case? API usually handles valid payloads.
        url_del = f"{base_url}/docs/{doc_id}/tables/_grist_ACLRules/data/delete"
        requests.post(url_del, headers=HEADERS, json=ids_to_del)
    
    # 2. Prepare new records
    records_to_add = []
    
    # Cache resources to avoid re-fetching per rule
    # Actually, find_or_create does a fetch. To optimize, we should fetch once.
    # Let's just trust find_or_create for now, or optimizing is better.
    # Simple optimization: Fetch all resources once, build map.
    all_res = fetch_table_records(base_url, doc_id, '_grist_ACLResources')
    res_map = {} # Key: "tid|cids" -> ID
    for r in all_res:
        rf = r['fields']
        k = f"{rf.get('tableId') or '*'}|{rf.get('colIds') or '*'}"
        res_map[k] = r['id']
        
    for i, rule in enumerate(new_rules_json):
        # Resolve Resource
        r_str = rule.get('Recurso', 'Geral')
        # Parse
        if "[" in r_str and r_str.endswith("]"):
            parts = r_str.split(" [")
            tid = parts[0].strip()
            cids = parts[1].rstrip("]").strip()
        else:
            tid = r_str.strip()
            cids = "*"
            
        key = f"{tid}|{cids}"
        res_id = res_map.get(key)
        
        if not res_id:
            # Create
            url_res = f"{base_url}/docs/{doc_id}/tables/_grist_ACLResources/records"
            payload = {'records': [{'fields': {'tableId': tid, 'colIds': cids}}]}
            resp = requests.post(url_res, headers=HEADERS, json=payload)
            if resp.status_code == 200:
                new_id = resp.json()['records'][0]['id']
                res_map[key] = new_id
                res_id = new_id
            else:
                raise Exception(f"Falha ao criar recurso {r_str}: {resp.text}")

        # Build Rule Record
        records_to_add.append({
            'fields': {
                'resource': res_id,
                'aclFormula': rule.get('Condição', ''),
                'permissionsText': rule.get('Permissões', ''),
                'memo': rule.get('Memo', ''),
                'rulePos': i + 1 # Force strict ordering
            }
        })
        
    # 3. Batch Insert
    if records_to_add:
        url_add = f"{base_url}/docs/{doc_id}/tables/_grist_ACLRules/records"
        requests.post(url_add, headers=HEADERS, json={'records': records_to_add})

    return True

# --- ... inside Tab 4 ... ---
with tab4:
    st.header("🛡️ Auditoria de Regras (Access Rules)")
    st.info("Visualização avançada das regras de acesso (tabelas _grist_ACLRules e _grist_ACLResources).")
    
    # ... doc selector (re-use existing) ...
    if st.session_state.mapped_data is not None:
        all_docs_list = st.session_state.mapped_data[['Documento', 'Doc ID']].drop_duplicates()
        doc_opts_r = {r['Documento']: r['Doc ID'] for _, r in all_docs_list.iterrows()}
    else:
        wss = get_workspaces_and_docs(CURRENT_BASE_URL, selected_org_id)
        doc_opts_r = {}
        for ws in wss:
            for d in ws.get('docs', []):
                doc_opts_r[d['name']] = d['id']
    
    target_r_name = st.selectbox("Selecionar Documento para Auditoria", sorted(doc_opts_r.keys()), index=None, key="acl_doc_sel_audit")
    
    if target_r_name:
        target_r_id = doc_opts_r[target_r_name]
        
        # SUB-TABS
        sub_t1, sub_t2 = st.tabs(["👁️ Visualizar", "✍️ Editar Regras"])
        
        with sub_t1:
            if st.button("🔍 Carregar Regras", key="btn_load_acl_audit"):
                with st.spinner("Buscando metadados de regras..."):
                    data = get_denormalized_rules(CURRENT_BASE_URL, target_r_id)
                    st.session_state.acl_audit_data = data
                    if not data:
                        st.warning("Nenhuma regra encontrada ou erro de permissão.")
                    else:
                        st.success(f"{len(data)} regras encontradas!")

            if 'acl_audit_data' in st.session_state and st.session_state.acl_audit_data:
                df_rules = pd.DataFrame(st.session_state.acl_audit_data)
                
                # Filtros
                f_rec = st.text_input("Filtrar por Recurso (Tabela)", key="audit_filter_rec")
                if f_rec:
                    df_rules = df_rules[df_rules['Recurso'].str.contains(f_rec, case=False, na=False)]

                st.dataframe(
                    df_rules,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "ID Regra": None, # Hide ID
                        "Posição": None,
                        "Memo": st.column_config.TextColumn("Descrição/Memo", width="medium"),
                        "Recurso": st.column_config.TextColumn("Recurso", width="medium"),
                        "Condição": st.column_config.TextColumn("Fórmula de Condição", width="large"),
                        "Permissões": st.column_config.TextColumn("Permissões", width="small"),
                    }
                )

                # --- EXPORT SECTION ---
                st.divider()
                st.subheader("📥 Exportar para IA (JSON)")
                
                import json
                export_data = df_rules.to_dict(orient='records')
                # Remove internal ID for export cleanliness
                for d in export_data:
                    d.pop('ID Regra', None)
                    d.pop('Posição', None) # We rely on list order implicitly or re-gen it
                    
                json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
                
                st.download_button(
                    label="💾 Baixar JSON de Regras",
                    data=json_str,
                    file_name=f"regras_{target_r_name.replace(' ', '_')}.json",
                    mime="application/json"
                )
                
                st.text_area("JSON para Copiar", value=json_str, height=300, key="acl_json_export_area")

        with sub_t2:
            st.header("Modificar Regras")
            st.warning("⚠️ Cuidado: Esta operação substitui TODAS as regras do documento.")
            
            edit_json = st.text_area("Cole o novo JSON de regras aqui:", height=400, key="edit_json_area")
            
            if st.button("📤 Enviar Regras para o Grist", type="primary"):
                if not edit_json.strip():
                    st.error("JSON vazio!")
                else:
                    try:
                        import json
                        new_rules = json.loads(edit_json)
                        
                        # 1. Backup Current
                        st.info("Criando backup das regras atuais...")
                        current_data = get_denormalized_rules(CURRENT_BASE_URL, target_r_id)
                        ok_bkp, path_bkp = backup_rules_locally(target_r_name, current_data)
                        
                        if ok_bkp:
                            st.success(f"Backup salvo em: {path_bkp}")
                            
                            # 2. Apply
                            with st.spinner("Aplicando novas regras..."):
                                apply_denormalized_rules(CURRENT_BASE_URL, target_r_id, new_rules)
                                st.balloons()
                                st.success("Regras atualizadas com sucesso! Verifique na aba 'Visualizar'.")
                                st.cache_data.clear()
                        else:
                            st.error(f"Falha no backup: {path_bkp}. Operação abortada.")
                            
                    except json.JSONDecodeError:
                        st.error("Erro: JSON inválido.")
                    except Exception as e:
                        st.error(f"Erro ao aplicar regras: {e}")

# --- TAB 5: Ajuda ---
with tab5:
    st.markdown("""
    # 📘 Manual de Ajuda - Gestor PQC

    Bem-vindo ao **Gestor de Acessos PQC-RS**. Esta ferramenta foi desenvolvida para facilitar a administração de permissões, usuários e regras de acesso (ACL) dentro da sua organização Grist.

    ---

    ## 🚀 Primeiros Passos

    ### 1. Seleção de Organização
    Na barra lateral esquerda (**Sidebar**), você encontra o menu de configuração.
    - **Selecione a Organização**: Escolha qual organização Grist você deseja gerenciar. O sistema tenta selecionar automaticamente a "Qualidade Contábil" se disponível.
    - **Base URL**: O sistema ajusta automaticamente a URL da API (ex: `docs.getgrist.com` ou domínios personalizados).
    - **Forçar Recarga**: Use este botão se você fez alterações fora do sistema e quer garantir que os dados exibidos estejam 100% atualizados, limpando o cache local.

    ---

    ## 🛠️ Funcionalidades por Aba

    ### 👥 1. Visão Global (Org)
    Esta aba mostra todos os usuários que têm acesso à organização como um todo (não necessariamente a documentos específicos, mas ao "Team Site").
    - **Filtros**: Use os campos de texto para buscar por Nome ou Email.
    - **Dados**: Exibe Nome, Email e o Nível de Acesso Global.

    ### 🗺️ 2. Mapeamento de Documentos
    Esta é a ferramenta mais poderosa para auditoria em massa.
    1. **Botão "Iniciar Mapeamento Completo"**: Varre **todos** os workspaces e documentos da organização selecionada. Isso pode levar alguns segundos.
    2. **Tabela de Resultados**: Lista cada combinação de Usuário x Documento.
       - Usuários "Indefinidos" aparecem se o documento não tiver usuários explícitos listados na API de acesso.
    3. **Filtros**:
       - **Ocultar herdados**: Esconde acessos que vêm da organização/workspace, focando em acessos diretos.
       - Filtros por Doc, Email, Nome e Acesso.
    4. **Edição e Seleção**: Marque a caixa "Sel" (Selecionar) ao lado dos itens que deseja modificar.
    5. **📦 Operações em Massa** (aparecem após selecionar itens):
       - **📄 Copiar**: Copia o acesso dos usuários selecionados para um **Documento Destino**.
       - **🚚 Mover**: Copia o acesso para o destino e **remove** do documento original.
       - **✏️ Atualizar Nível**: Altera o papel (Viewer, Editor, Owner) dos usuários selecionados no documento atual.
       - **🗑️ Remover**: Remove o acesso dos usuários selecionados.

    ### ⚡ 3. Ações Rápidas
    Ideal para ajustes pontuais sem precisar rodar o mapeamento completo.
    - **Selecionar Documento**: Escolha o arquivo alvo.
    - **🟢 Adicionar**: Insira um email e escolha o nível (Viewer, Editor, Owner) para conceder acesso imediato.
    - **🔴 Remover**: Digite o email para revogar o acesso imediatamente.

    ### 🏗️ 7. Clonador de Templates
    Esta ferramenta permite copiar a estrutura (esquema) de uma tabela de um documento para outros.
    - **Origem**: Escolha o documento e a tabela que servem de modelo (ex: `Checklistdiamante`).
    - **Destinos**: Selecione um ou mais documentos onde você deseja que essa tabela seja criada.
    - **O que é copiado**: IDs das colunas, Nomes (Labels), Tipos de dados (Text, Numeric, Ref, etc), Fórmulas e Opções de Widget.
    - **O que NÃO é copiado**: Os dados (registros) da tabela.
    - **Nota**: Útil para padronizar documentos novos com as mesmas tabelas de suporte.

    ---

    ## 💡 Dicas e Solução de Problemas
    - **Cache**: O sistema guarda dados por 5 a 10 minutos para ser rápido. Se algo parecer desatualizado, use o botão **🔄 Forçar Recarga Geral** na barra lateral.
    - **Permissões**: Para ler ou escrever regras (Aba 4), seu usuário da API (`GRIST_API_KEY`) deve ser **DONO (Owner)** do documento.
    - **Erros de API**: Verifique se sua chave API no arquivo `.env` está correta e tem as permissões necessárias.
    """)

# --- TAB 6: Auditoria de Integridade ---
with tab6:
    st.header("⚖️ Auditoria de Integridade")
    st.markdown("Auditoria avançada comparando acessos reais com múltiplas colunas de referência.")

    # --- CONFIGURATION MANAGEMENT ---
    saved_configs = load_audit_configs()
    config_names = ["(Nova Configuração)"] + list(saved_configs.keys())
    
    col_cfg1, col_cfg2 = st.columns([3, 1])
    sel_config_name = col_cfg1.selectbox("📂 Carregar Configuração Salva", config_names, key="audit_config_loader")
    
    # Initialize session state for config inputs if loading
    if sel_config_name != "(Nova Configuração)":
        cfg = saved_configs[sel_config_name]
        # We store these temporarily to pre-fill, but selects depend on dynamic API calls
        # so we handle the defaults inside the widgets below using 'index' logic where possible
        # or just letting the user see the values.
        # Ideally, we set indices.
        pass

    st.divider()

    # --- SETUP FORM ---
    
    # 1. Document
    if st.session_state.mapped_data is not None:
        all_docs_list = st.session_state.mapped_data[['Documento', 'Doc ID']].drop_duplicates()
        doc_opts_audit = {r['Documento']: r['Doc ID'] for _, r in all_docs_list.iterrows()}
    else:
        wss = get_workspaces_and_docs(CURRENT_BASE_URL, selected_org_id)
        doc_opts_audit = {}
        for ws in wss:
            for d in ws.get('docs', []):
                doc_opts_audit[d['name']] = d['id']
    
    # Try to match loaded config
    def_doc_idx = None
    loaded_doc_id = None
    if sel_config_name != "(Nova Configuração)":
        loaded_doc_id = saved_configs[sel_config_name].get("doc_id")
        # Find index
        keys_d = sorted(doc_opts_audit.keys())
        for i, k in enumerate(keys_d):
            if doc_opts_audit[k] == loaded_doc_id:
                def_doc_idx = i
                break

    sel_doc_audit = st.selectbox("1. Documento Alvo", sorted(doc_opts_audit.keys()), index=def_doc_idx, key="audit_doc_sel")

    if sel_doc_audit:
        doc_id_audit = doc_opts_audit[sel_doc_audit]
        
        # 2. Table
        tables = get_tables(CURRENT_BASE_URL, doc_id_audit)
        table_opts = {t['id']: t['id'] for t in tables}
        
        def_tbl_idx = None
        if sel_config_name != "(Nova Configuração)":
            saved_tbl = saved_configs[sel_config_name].get("table_id")
            if saved_tbl in table_opts:
                keys_t = sorted(table_opts.keys())
                if saved_tbl in keys_t:
                    def_tbl_idx = keys_t.index(saved_tbl)

        sel_table_audit = st.selectbox("2. Tabela de Referência", sorted(table_opts.keys()), index=def_tbl_idx, key="audit_table_sel")
        
        if sel_table_audit:
            # 3. Columns
            cols = get_columns(CURRENT_BASE_URL, doc_id_audit, sel_table_audit)
            col_opts = {c['id']: c['fields']['label'] for c in cols}
            col_map_rev = {v: k for k, v in col_opts.items()}
            sorted_col_labels = sorted(col_opts.values())

            # Load defaults
            def_title_idx = None
            def_emails = []
            if sel_config_name != "(Nova Configuração)":
                c = saved_configs[sel_config_name]
                s_title_id = c.get("title_col")
                s_email_ids = c.get("email_cols", [])
                
                # Title index
                if s_title_id and s_title_id in col_opts:
                    lbl = col_opts[s_title_id]
                    if lbl in sorted_col_labels:
                        def_title_idx = sorted_col_labels.index(lbl)
                
                # Email multiselect
                for eid in s_email_ids:
                    if eid in col_opts:
                        def_emails.append(col_opts[eid])

            c1, c2 = st.columns(2)
            sel_title_label = c1.selectbox("3. Coluna de Título (ex: Empresa)", sorted_col_labels, index=def_title_idx, key="audit_col_title")
            sel_email_labels = c2.multiselect("4. Colunas de E-mail (Avaliadores etc)", sorted_col_labels, default=def_emails, key="audit_col_emails")
            
            # --- REFERENCE RESOLUTION LOGIC ---
            col_types = {c['id']: c['fields']['type'] for c in cols} # ID -> Type (e.g., 'Ref:Users')
            
            ref_configs = {} # Store resolution config: {SourceColID: {'target_table': Tbl, 'target_col': ColID}}
            
            if sel_email_labels:
                for label in sel_email_labels:
                    cid = col_map_rev.get(label)
                    ctype = col_types.get(cid, "")
                    if ctype.startswith("Ref:"):
                        ref_table = ctype.split(":")[1]
                        st.info(f"🔗 Coluna '{label}' é uma referência para a tabela '{ref_table}'.")
                        
                        # Fetch cols of target table to let user pick the email field
                        # We use a unique key for the selectbox based on label
                        ref_cols_raw = get_columns(CURRENT_BASE_URL, doc_id_audit, ref_table)
                        ref_col_opts = {rc['id']: rc['fields']['label'] for rc in ref_cols_raw}
                        
                        # Try to guess 'Email'
                        def_ref_idx = None
                        sorted_rc = sorted(ref_col_opts.values())
                        for i, rcl in enumerate(sorted_rc):
                            if "email" in rcl.lower():
                                def_ref_idx = i
                                break
                        
                        target_col_label = st.selectbox(f"Selecione a coluna de E-mail em '{ref_table}' para '{label}':", 
                                                      sorted_rc, 
                                                      index=def_ref_idx,
                                                      key=f"ref_res_{cid}")
                        
                        if target_col_label:
                            # Reverse lookup target col ID
                            target_col_id = [k for k,v in ref_col_opts.items() if v == target_col_label][0]
                            ref_configs[cid] = {
                                "target_table": ref_table,
                                "target_col": target_col_id
                            }

            # --- MANUAL REF CONFIG (For 'Any' types or undetected refs) ---
            with st.expander("⚙️ Configurar Referências Manuais (Se houver IDs numéricos)"):
                st.caption("Use isso se suas colunas mostram números (IDs) mas o sistema não detectou automaticamente (ex: Tipo 'Any').")
                
                # Dropdown to pick one of the selected email columns
                if sel_email_labels:
                    m_col_label = st.selectbox("Coluna para configurar:", ["(Selecione)"] + sel_email_labels, key="man_ref_col_sel")
                    if m_col_label != "(Selecione)":
                        m_cid = col_map_rev[m_col_label]
                        
                        # Fetch all tables to pick target
                        all_tables = get_tables(CURRENT_BASE_URL, doc_id_audit)
                        # tables have 'id'
                        # sort by id
                        all_tbl_ids = sorted([t['id'] for t in all_tables])
                        
                        m_target_table = st.selectbox("Tabela de Origem (que contém o email):", all_tbl_ids, key="man_ref_tbl_sel")
                        
                        if m_target_table:
                             # Fetch cols
                             m_ref_cols = get_columns(CURRENT_BASE_URL, doc_id_audit, m_target_table)
                             m_ref_opts = {rc['id']: rc['fields']['label'] for rc in m_ref_cols}
                             m_sorted_rc = sorted(m_ref_opts.values())
                             
                             m_target_col_label = st.selectbox("Coluna de Email na tabela origem:", m_sorted_rc, key="man_ref_target_col")
                             
                             if m_target_col_label:
                                 # Save to ref_configs
                                 m_target_col_id = [k for k,v in m_ref_opts.items() if v == m_target_col_label][0]
                                 
                                 # Overwrite/Set
                                 ref_configs[m_cid] = {
                                     "target_table": m_target_table,
                                     "target_col": m_target_col_id
                                 }
                                 st.success(f"Configurado: '{m_col_label}' -> '{m_target_table}.{m_target_col_label}'")

            # Save Config Section
            with st.expander("💾 Salvar esta configuração"):
                new_cfg_name = st.text_input("Nome da Configuração", value=sel_doc_audit if sel_config_name == "(Nova Configuração)" else sel_config_name)
                if st.button("Salvar Preset"):
                    if sel_title_label and sel_email_labels:
                         data = {
                             "doc_id": doc_id_audit,
                             "table_id": sel_table_audit,
                             "title_col": col_map_rev[sel_title_label],
                             "email_cols": [col_map_rev[l] for l in sel_email_labels],
                             # Save ref configs too if simple enough? For now simpler configs.
                             # Complex ref config persistence omitted for brevity, user re-selects or we improve later.
                         }
                         save_audit_config(new_cfg_name, data)
                         st.success("Salvo!")
                         time.sleep(1); st.rerun()

            if st.button("🔎 Executar Auditoria", type="primary"):
                if not sel_title_label or not sel_email_labels:
                    st.error("Selecione a coluna de título e pelo menos uma coluna de e-mail.")
                else:
                    with st.spinner("Cruzando dados..."):
                        title_col_id = col_map_rev[sel_title_label]
                        email_col_ids = [col_map_rev[l] for l in sel_email_labels]
                        
                        # Map label to ID for easy lookup
                        col_label_map = {col_map_rev[l]: l for l in sel_email_labels}
                        
                        # --- PRE-FETCH REFERENCE LOOKUPS ---
                        # Map: SourceColID -> { RefRowID -> ResolvedValue }
                        ref_lookups = {}
                        
                        for src_cid, cfg in ref_configs.items():
                            try:
                                t_recs = fetch_table_records(CURRENT_BASE_URL, doc_id_audit, cfg['target_table'])
                                lookup = {}
                                tgt_cid = cfg['target_col']
                                for r in t_recs:
                                    # Grist records have 'id'
                                    rid = r['id']
                                    val = r['fields'].get(tgt_cid)
                                    if val:
                                        lookup[rid] = str(val).strip().lower() # Normalize email
                                ref_lookups[src_cid] = lookup
                            except Exception as e:
                                st.error(f"Erro ao resolver referência para {cfg['target_table']}: {e}")

                        # A. Get Actual Explicit Access
                        doc_users = get_doc_users(CURRENT_BASE_URL, doc_id_audit)
                        actual_access_map = {} 
                        for u in doc_users:
                            if u.get('email') and u.get('access'):
                                actual_access_map[u['email'].strip().lower()] = u.get('access')
                        
                        # B. Get Reference Data
                        records = fetch_table_records(CURRENT_BASE_URL, doc_id_audit, sel_table_audit)
                        
                        # --- DEBUG SECTION ---
                        with st.expander("🕵️ Debug Dados (Resumido)"):
                            # Filter map for selected only
                            debug_map = {k: v for k, v in col_map_rev.items() if k == sel_title_label or k in sel_email_labels}
                            st.write("IDs das Colunas Selecionadas:", debug_map)
                            
                            # Show Types
                            types_debug = {label: col_types.get(col_map_rev.get(label), "N/A") for label in [sel_title_label] + sel_email_labels}
                            st.write("Tipos de Dados (Metadata):", types_debug)
                            
                            st.write("Configurações de Referência:", ref_configs)
                            
                            if records:
                                first_rec = records[0]['fields']
                                # Extract only relevant keys
                                filtered_rec = {}
                                for label in [sel_title_label] + sel_email_labels:
                                    cid = col_map_rev.get(label)
                                    if cid:
                                        filtered_rec[f"{label} ({cid})"] = first_rec.get(cid, "NÃO ENCONTRADO / VAZIO")
                                st.write("Dados do Primeiro Registro (Colunas Alvo):", filtered_rec)
                            else:
                                st.write("Nenhum registro encontrado na tabela.")
                        # ---------------------

                        # C. Build Matrix
                        table_data = []
                        matched_emails = set()
                        
                        # 1. Process Reference Table Rows
                        for r in records:
                            row_obj = {}
                            
                            # Title
                            row_title = r['fields'].get(title_col_id)
                            # Handle cases where title is list or complex object
                            if isinstance(row_title, list): row_title = str(row_title)
                            row_obj[sel_title_label] = row_title or ""
                            
                            # Process each selected Email Column
                            row_has_missing = False
                            missing_emails_in_row = [] # Store raw emails for fixing
                            
                            for col_id in email_col_ids:
                                col_label = col_label_map[col_id]
                                val = r['fields'].get(col_id)
                                
                                cell_display = []
                                
                                # Resolve Reference Value if needed
                                if col_id in ref_lookups and isinstance(val, int):
                                    # It's a single ref
                                    resolved = ref_lookups[col_id].get(val)
                                    val = resolved # Swap ID for Email String
                                elif col_id in ref_lookups and isinstance(val, list):
                                    # List of Refs? ['L', 1, 2]
                                    # Not common for single email cols, but possible
                                    pass # Logic below handles lists, but we need to resolve items.
                                    # Complex case, assuming single ref for now based on '56'.
                                
                                if val:
                                    # Extract emails
                                    cell_emails = []
                                    if isinstance(val, list):
                                        items = val[1:] if (len(val) > 0 and val[0] == 'L') else val
                                        for item in items:
                                            # If item is int and we have lookup
                                            if isinstance(item, int) and col_id in ref_lookups:
                                                r_val = ref_lookups[col_id].get(item)
                                                if r_val: cell_emails.append(r_val)
                                            elif isinstance(item, str): 
                                                cell_emails.append(item.strip().lower())
                                    elif isinstance(val, str):
                                        parts = val.split(",")
                                        for p in parts: cell_emails.append(p.strip().lower())
                                    elif isinstance(val, int) and col_id in ref_lookups:
                                         # Already resolved above? check double logic
                                         # Logic above 'val = resolved' handled strict replacement
                                         # If resolved is str, it goes to elif isinstance(val, str)
                                         # If logic above failed (lookup miss), it stays int
                                         pass
                                    
                                    # Check status
                                    for em in cell_emails:
                                        if em in actual_access_map:
                                            cell_display.append(f"✅ {em}")
                                            matched_emails.add(em)
                                        else:
                                            cell_display.append(f"🔴 {em}")
                                            missing_emails_in_row.append(em)
                                            row_has_missing = True
                                
                                # Join multiple emails in same cell with newlines or commas
                                row_obj[col_label] = "\n".join(cell_display)
                            
                            # Hidden metadata for actions
                            row_obj["_missing_emails"] = json.dumps(missing_emails_in_row)
                            row_obj["_orphan_email"] = None
                            row_obj["_type"] = "reference"
                            
                            table_data.append(row_obj)

                        # 2. Process Orphans (In Doc, Not in Table)
                        all_doc_emails = set(actual_access_map.keys())
                        orphans = sorted(list(all_doc_emails - matched_emails))
                        
                        first_email_col_label = sel_email_labels[0] # Put orphan in the first email col
                        
                        for orphan in orphans:
                            row_obj = {}
                            row_obj[sel_title_label] = "" # Blank Title
                            
                            # Fill first col with orphan info
                            row_obj[first_email_col_label] = f"☢️ {orphan}"
                            
                            # Fill other cols blank
                            for lbl in sel_email_labels[1:]:
                                row_obj[lbl] = ""
                            
                            # Metadata
                            row_obj["_missing_emails"] = "[]"
                            row_obj["_orphan_email"] = orphan
                            row_obj["_type"] = "orphan"
                            
                            table_data.append(row_obj)
                            
                        # D. Display
                        if not table_data:
                            st.info("Nenhum dado encontrado.")
                        else:
                            df_res = pd.DataFrame(table_data)
                            
                            st.caption("Selecione as linhas abaixo para aplicar correções em massa.")
                            
                            # Add selection column
                            df_res.insert(0, "Selecionar", False)
                            
                            # Configure columns (Hide metadata by excluding from order or implicit handling)
                            # We will use column_order to show only relevant columns
                            
                            # Reorder: Select, Title, Emails...
                            cols_visible = ["Selecionar", sel_title_label] + sel_email_labels
                            
                            edited_df = st.data_editor(
                                df_res,
                                column_order=cols_visible,
                                disabled=[sel_title_label] + sel_email_labels, # Disable content editing
                                use_container_width=True,
                                hide_index=True,
                                key="audit_editor"
                            )
                            
                            # E. Actions based on selection
                            selected_rows = edited_df[edited_df["Selecionar"]]
                            
                            if not selected_rows.empty:
                                st.divider()
                                c_act1, c_act2 = st.columns(2)
                                
                                # Gather Data
                                to_grant = []
                                to_revoke = []
                                
                                for _, row in selected_rows.iterrows():
                                    # Type 1: Missing (Grant)
                                    if row["_type"] == "reference":
                                        missing = json.loads(row["_missing_emails"])
                                        to_grant.extend(missing)
                                    
                                    # Type 2: Orphan (Revoke)
                                    if row["_type"] == "orphan":
                                        if row["_orphan_email"]:
                                            to_revoke.append(row["_orphan_email"])
                                
                                to_grant = list(set(to_grant))
                                to_revoke = list(set(to_revoke))
                                
                                with c_act1:
                                    if to_grant:
                                        st.write(f"🔴 **{len(to_grant)} usuários para CONCEDER acesso (Viewer):**")
                                        st.code("\n".join(to_grant))
                                        if st.button("✨ Conceder Acesso Selecionado", key="btn_audit_grant"):
                                            progress = st.progress(0)
                                            for i, em in enumerate(to_grant):
                                                update_doc_access(CURRENT_BASE_URL, doc_id_audit, em, "viewers")
                                                progress.progress((i+1)/len(to_grant))
                                            st.success("Acessos concedidos!")
                                            time.sleep(1); st.rerun()
                                    else:
                                        st.info("Nenhuma correção de acesso pendente na seleção.")

                                with c_act2:
                                    if to_revoke:
                                        st.write(f"☢️ **{len(to_revoke)} usuários para REMOVER acesso:**")
                                        st.code("\n".join(to_revoke))
                                        if st.button("🗑️ Remover Acesso Selecionado", type="primary", key="btn_audit_revoke"):
                                            progress = st.progress(0)
                                            for i, em in enumerate(to_revoke):
                                                update_doc_access(CURRENT_BASE_URL, doc_id_audit, em, None)
                                                progress.progress((i+1)/len(to_revoke))
                                            st.success("Acessos removidos!")
                                            time.sleep(1); st.rerun()
                                    else:
                                        st.info("Nenhum usuário órfão na seleção.")

# --- TAB 7: Template Cloner ---
with tab7:
    st.header("🏗️ Clonador de Templates (Estrutura de Tabelas)")
    st.markdown("Copie a estrutura (colunas e fórmulas) de uma tabela para outros documentos, sem copiar os dados.")

    if st.session_state.mapped_data is not None:
        all_docs_list = st.session_state.mapped_data[['Documento', 'Doc ID']].drop_duplicates()
        doc_opts_clone = {r['Documento']: r['Doc ID'] for _, r in all_docs_list.iterrows()}
    else:
        wss = get_workspaces_and_docs(CURRENT_BASE_URL, selected_org_id)
        doc_opts_clone = {}
        for ws in wss:
            for d in ws.get('docs', []):
                doc_opts_clone[d['name']] = d['id']
    
    st.subheader("1. Selecione a Origem")
    col_src1, col_src2 = st.columns(2)
    src_doc_name = col_src1.selectbox("Documento de Origem", sorted(doc_opts_clone.keys()), index=None, key="clone_src_doc")
    
    if src_doc_name:
        src_doc_id = doc_opts_clone[src_doc_name]
        src_tables = get_tables(CURRENT_BASE_URL, src_doc_id)
        src_table_ids = sorted([t['id'] for t in src_tables])
        src_table_id = col_src2.selectbox("Tabela de Origem", src_table_ids, index=None, key="clone_src_table")
        
        if src_table_id:
            # Fetch Schema
            with st.status("Lendo estrutura da tabela...", expanded=False):
                raw_cols = get_columns(CURRENT_BASE_URL, src_doc_id, src_table_id)
                
                # Filter out system columns and internal metadata
                # Grist API returns 'id' and 'fields'
                clean_cols = []
                for c in raw_cols:
                    f = c['fields']
                    # We only need key functional fields for cloning
                    clean_cols.append({
                        "id": c['id'],
                        "fields": {
                            "label": f.get("label"),
                            "type": f.get("type"),
                            "isFormula": f.get("isFormula", False),
                            "formula": f.get("formula", ""),
                            "widgetOptions": f.get("widgetOptions", ""),
                            "description": f.get("description", "")
                        }
                    })
                st.write(f"Encontradas {len(clean_cols)} colunas.")
                st.json(clean_cols)

            st.subheader("2. Selecione os Destinos")
            # Multiple selection for targets
            target_doc_names = st.multiselect("Documentos de Destino", sorted(doc_opts_clone.keys()), key="clone_targets")
            
            if target_doc_names:
                st.warning(f"⚠️ Isso criará a tabela '{src_table_id}' em {len(target_doc_names)} documentos. Se a tabela já existir, a criação da tabela falhará, mas tentaremos adicionar as colunas faltantes.")
                
                if st.button("🚀 Iniciar Clonagem em Massa", type="primary"):
                    progress = st.progress(0)
                    log_area = st.empty()
                    logs = []
                    
                    for i, t_name in enumerate(target_doc_names):
                        t_id = doc_opts_clone[t_name]
                        logs.append(f"--- Processando: {t_name} ---")
                        
                        # 1. Try to create Table WITH columns in one go
                        ok_t, msg_t = create_table(CURRENT_BASE_URL, t_id, src_table_id, clean_cols)
                        
                        if ok_t:
                            logs.append(f"✅ {msg_t}")
                        elif msg_t == "EXISTING":
                            logs.append(f"ℹ️ Tabela '{src_table_id}' já existe. Verificando colunas...")
                            # 2. Add Columns only (Grist will skip existing ones if we are lucky, 
                            # or we can try to be safe and just log it)
                            ok_c, msg_c = add_columns(CURRENT_BASE_URL, t_id, src_table_id, clean_cols)
                            logs.append(f"Colunas: {msg_c}")
                        else:
                            logs.append(f"❌ {msg_t}")
                        
                        progress.progress((i + 1) / len(target_doc_names))
                        log_area.code("\n".join(logs))
                    
                    st.success("Processo de clonagem concluído!")
    else:
        st.info("Selecione um documento de origem para começar.")

# --- TAB 8: Blueprint (Novo Doc) ---
with tab8:
    st.header("🛠️ Criar Estrutura (Blueprint)")
    st.markdown("Crie novos documentos do zero e aplique uma estrutura de tabelas e colunas via JSON.")

    # 1. DOCUMENT CREATION SECTION
    st.subheader("1. Criar Novo Documento")
    col_c1, col_c2 = st.columns([2, 1])
    
    new_doc_name = col_c1.text_input("Nome do Novo Documento", placeholder="Ex: PQC 2026 - Novo Doc", key="bp_new_doc_input")
    
    # Get Workspaces for selection
    workspaces_raw = get_workspaces_and_docs(CURRENT_BASE_URL, selected_org_id)
    ws_opts = {ws['name']: ws['id'] for ws in workspaces_raw}
    sel_ws_name = col_c2.selectbox("Workspace Destino", sorted(ws_opts.keys()), key="blueprint_ws_sel")

    if st.button("🆕 Criar Documento Vazio", type="secondary", key="btn_create_empty_doc"):
        if not new_doc_name:
            st.error("Informe o nome do documento.")
        else:
            ws_id = ws_opts[sel_ws_name]
            with st.spinner(f"Criando documento '{new_doc_name}'..."):
                ok_doc, res_doc = create_document(CURRENT_BASE_URL, ws_id, new_doc_name)
                if ok_doc:
                    st.success(f"✅ Documento criado com sucesso! ID: {res_doc}")
                    st.session_state.last_created_doc_id = res_doc
                    st.session_state.last_created_doc_name = new_doc_name
                    # Não usamos st.rerun() aqui para evitar voltar para a aba 1
                    # Apenas limpamos o cache de documentos para a próxima recarga natural
                    st.cache_data.clear()
                else:
                    st.error(f"❌ Falha ao criar documento: {res_doc}")

    st.divider()

    # 2. BLUEPRINT APPLICATION SECTION
    st.subheader("2. Aplicar Estrutura (Blueprint JSON)")
    
    # Selection of Target Document
    doc_opts_bp = {}
    if st.session_state.mapped_data is not None:
        all_docs_list = st.session_state.mapped_data[['Documento', 'Doc ID']].drop_duplicates()
        doc_opts_bp = {r['Documento']: r['Doc ID'] for _, r in all_docs_list.iterrows()}
    else:
        for ws in workspaces_raw:
            for d in ws.get('docs', []):
                doc_opts_bp[d['name']] = d['id']
    
    # Injetar o documento recém criado se existir
    if 'last_created_doc_id' in st.session_state:
        doc_name_label = f"✨ Recém Criado ({st.session_state.get('last_created_doc_name', 'Novo')})"
        doc_opts_bp[doc_name_label] = st.session_state.last_created_doc_id

    sel_target_doc_name = st.selectbox("Selecione o Documento Alvo", sorted(doc_opts_bp.keys(), reverse=True), key="blueprint_target_doc")
    
    col_bp_actions1, col_bp_actions2 = st.columns([1, 1])
    with col_bp_actions1:
        overwrite_mode = st.checkbox("🔥 Modo Sobrescrita (Apagar tabelas atuais)", help="Se marcado, todas as tabelas atuais (exceto as de sistema) serão APAGADAS antes de aplicar o novo JSON. USE COM CAUTELA!")
        if overwrite_mode:
            st.warning("⚠️ Você ativou a limpeza total. Isso apagará todos os dados das tabelas atuais do documento selecionado.")
            confirm_overwrite = st.checkbox("✅ Confirmo que desejo APAGAR todas as tabelas do documento selecionado.", key="confirm_ow")
        else:
            confirm_overwrite = False
    
    if st.button("🔍 Buscar Estrutura Atual (JSON)", key="btn_fetch_blueprint"):
        if not sel_target_doc_name:
            st.error("Selecione um documento alvo.")
        else:
            with st.spinner("Extraindo estrutura do documento..."):
                t_id = doc_opts_bp[sel_target_doc_name]
                tables = get_tables_no_cache(CURRENT_BASE_URL, t_id)
                blueprint_fetch = {"tables": []}
                for t in tables:
                    if t['id'].startswith('_grist'): continue
                    cols = get_columns_no_cache(CURRENT_BASE_URL, t_id, t['id'])
                    clean_cols = []
                    for c in cols:
                        f = c['fields']
                        w_opts = f.get("widgetOptions", "{}")
                        try:
                            w_dict = json.loads(w_opts) if w_opts else {}
                        except:
                            w_dict = {}
                            
                        col_entry = {
                            "id": c['id'],
                            "label": f.get("label"),
                            "type": f.get("type"),
                            "isFormula": f.get("isFormula", False),
                            "formula": f.get("formula", "")
                        }
                        
                        # Extract choices if they exist
                        if "choices" in w_dict:
                            col_entry["options"] = w_dict["choices"]
                            
                        clean_cols.append(col_entry)
                    blueprint_fetch["tables"].append({
                        "id": t['id'],
                        "columns": clean_cols
                    })
                
                # Update text area directly via session state
                fetched_json = json.dumps(blueprint_fetch, indent=2, ensure_ascii=False)
                st.session_state["bp_json_area"] = fetched_json
                st.success(f"Estrutura carregada! Encontradas {len(blueprint_fetch['tables'])} tabelas.")
                # st.rerun()  <-- REMOVIDO PARA EVITAR PULO DE ABA

    blueprint_json_raw = st.text_area("Cole o JSON de estrutura:", 
                                    height=400, 
                                    key="bp_json_area",
                                    placeholder='''{
  "tables": [
    {
      "id": "Tabela1",
      "columns": [
        {"id": "Nome", "type": "Text", "label": "Nome"}
      ]
    }
  ]
}''')

    if st.button("🚀 Executar Blueprint", type="primary", key="btn_exec_blueprint"):
        if not blueprint_json_raw.strip():
            st.error("O campo JSON está vazio.")
        elif not sel_target_doc_name:
            st.error("Selecione um documento alvo.")
        else:
            try:
                raw_data = json.loads(blueprint_json_raw)
                
                # Suporte para {"tables": [...]} ou [...]
                if isinstance(raw_data, dict) and "tables" in raw_data:
                    blueprint_data = raw_data["tables"]
                elif isinstance(raw_data, list):
                    blueprint_data = raw_data
                else:
                    st.error("Formato JSON inválido. Deve ser uma lista de tabelas ou um objeto com a chave 'tables'.")
                    st.stop()

                target_doc_id = doc_opts_bp[sel_target_doc_name]
                progress_bp = st.progress(0.0)
                logs_bp = []
                
                # 0. Fetch existing structure to avoid duplicates
                existing_tables = get_tables_no_cache(CURRENT_BASE_URL, target_doc_id)
                existing_table_ids = {t['id'] for t in existing_tables}
                
                with st.status("Executando Blueprint em 2 etapas...", expanded=True) as status_container:
                    
                    # --- OPCIONAL: SOBRESCRITA (APAGAR TUDO) ---
                    if overwrite_mode:
                        status_container.write("### 🔥 Etapa 0: Limpando Documento (Sobrescrita)")
                        tables_to_del = [tid for tid in existing_table_ids if not tid.startswith('_grist')]
                        
                        if tables_to_del:
                            status_container.write(f"🗑️ Removendo {len(tables_to_del)} tabelas em lote...")
                            ok_del, msg_del = delete_tables_batch(CURRENT_BASE_URL, target_doc_id, tables_to_del)
                            if ok_del:
                                logs_bp.append(f"🗑️ {msg_del}")
                            else:
                                logs_bp.append(f"⚠️ Erro ao limpar documento: {msg_del}")
                        
                        # Refresh existing list after deletion
                        existing_tables = get_tables_no_cache(CURRENT_BASE_URL, target_doc_id)
                        existing_table_ids = {t['id'] for t in existing_tables}

                    # --- ETAPA 1: CRIAR TABELAS (ESQUELETO SEM REFS) ---
                    status_container.write("### 🏗️ Etapa 1: Criando/Verificando Tabelas")
                    for i, tbl in enumerate(blueprint_data):
                        t_id = tbl.get('id')
                        t_cols_all = tbl.get('columns', [])
                        
                        # Check if table exists
                        if t_id in existing_table_ids:
                            logs_bp.append(f"ℹ️ {t_id}: Tabela já existe. Verificando colunas...")
                            
                            # Get existing columns for this table
                            ex_cols = get_columns_no_cache(CURRENT_BASE_URL, target_doc_id, t_id)
                            ex_col_ids = {c['id'] for c in ex_cols}
                            
                            # Filter only NEW columns
                            new_cols_to_add = []
                            for col in t_cols_all:
                                if col['id'] not in ex_col_ids and not str(col.get('type', '')).startswith('Ref:'):
                                    new_cols_to_add.append({
                                        "id": col['id'],
                                        "fields": {
                                            "label": col.get('label', col['id']),
                                            "type": col.get('type', 'Text'),
                                            "isFormula": col.get('isFormula', False),
                                            "formula": col.get('formula', '')
                                        }
                                    })
                            
                            if new_cols_to_add:
                                status_container.write(f"⏳ Adicionando {len(new_cols_to_add)} colunas novas em **{t_id}**...")
                                ok_c, msg_c = add_columns(CURRENT_BASE_URL, target_doc_id, t_id, new_cols_to_add)
                                logs_bp.append(f"   - Colunas novas: {msg_c}")
                            else:
                                logs_bp.append(f"   - Nenhuma coluna nova para adicionar.")
                                
                        else:
                            # Table DOES NOT exist, create it
                            # Filtrar apenas colunas que NÃO são Ref para o esqueleto
                            t_cols_skeleton = [
                                c for c in t_cols_all 
                                if not str(c.get('type', '')).startswith('Ref:')
                            ]
                            
                            status_container.write(f"🆕 Criando nova tabela: **{t_id}**...")
                            
                            formatted_skeleton = []
                            for col in t_cols_skeleton:
                                f_payload = {
                                    "label": col.get('label', col['id']),
                                    "type": col.get('type', 'Text'),
                                    "isFormula": col.get('isFormula', False),
                                    "formula": col.get('formula', '')
                                }
                                # Add choices if present
                                if "options" in col:
                                    f_payload["widgetOptions"] = json.dumps({"choices": col["options"]})
                                    
                                formatted_skeleton.append({
                                    "id": col['id'],
                                    "fields": f_payload
                                })

                            ok_bp, msg_bp = create_table(CURRENT_BASE_URL, target_doc_id, t_id, formatted_skeleton)
                            if ok_bp:
                                logs_bp.append(f"✅ {t_id}: Tabela criada.")
                            else:
                                logs_bp.append(f"❌ {t_id}: Erro ao criar - {msg_bp}")
                    
                    progress_bp.progress(0.5)
                    
                    # --- ETAPA 2: ADICIONAR COLUNAS DE REFERÊNCIA ---
                    status_container.write("### 🔗 Etapa 2: Vinculando Colunas de Referência")
                    for i, tbl in enumerate(blueprint_data):
                        t_id = tbl.get('id')
                        t_cols_all = tbl.get('columns', [])
                        
                        # Get current columns again to be safe
                        curr_cols = get_columns_no_cache(CURRENT_BASE_URL, target_doc_id, t_id)
                        curr_col_ids = {c['id'] for c in curr_cols}
                        
                        t_cols_refs = [
                            c for c in t_cols_all 
                            if str(c.get('type', '')).startswith('Ref:') and c['id'] not in curr_col_ids
                        ]
                        
                        if t_cols_refs:
                            formatted_refs = []
                            for col in t_cols_refs:
                                formatted_refs.append({
                                    "id": col['id'],
                                    "fields": {
                                        "label": col.get('label', col['id']),
                                        "type": col.get('type'),
                                        "isFormula": col.get('isFormula', False),
                                        "formula": col.get('formula', '')
                                    }
                                })
                            
                            status_container.write(f"🔗 Vinculando refs em: **{t_id}**...")
                            ok_c, msg_c = add_columns(CURRENT_BASE_URL, target_doc_id, t_id, formatted_refs)
                            if ok_c:
                                logs_bp.append(f"🔗 {t_id}: Referências novas OK.")
                            else:
                                logs_bp.append(f"❌ {t_id}: Falha nas Refs - {msg_c}")
                    progress_bp.progress(1.0)
                    status_container.update(label="Processo Concluído!", state="complete")
                
                st.success("Blueprint aplicado!")
                with st.expander("📄 Ver Log Detalhado"):
                    st.code("\n".join(logs_bp))
            except Exception as e:
                st.error(f"💥 Erro na execução: {e}")
                with st.expander("🛠️ Debug Técnico (Traceback)"):
                    import traceback
                    st.code(traceback.format_exc())

    # --- DEBUG AREA AT THE BOTTOM ---
    st.divider()
    with st.expander("🔍 Debug do Estado da Aba"):
        st.write("Documento Recém Criado ID:", st.session_state.get('last_created_doc_id', 'Nenhum'))
        if blueprint_json_raw:
            try:
                st.write("Status do JSON:", "✅ Válido" if json.loads(blueprint_json_raw) else "⚠️ Vazio")
            except:
                st.write("Status do JSON: ❌ Erro de Sintaxe")

@st.cache_data(ttl=300)
def get_real_data_size(base_url, doc_id):
    """Fetches the actual SQLite file size (no history) using HEAD request on download endpoint."""
    try:
        # Use nohistory=true to get only the data size (Grist 10MB limit target)
        url = f"{base_url}/docs/{doc_id}/download?nohistory=true"
        # We use a GET with stream=True but don't download the body to get the header
        with requests.get(url, headers=HEADERS, stream=True) as r:
            if r.status_code == 200:
                size = r.headers.get('Content-Length')
                return int(size) if size else 0
        return 0
    except Exception:
        return 0

# --- TAB 9: Limites e Uso ---
with tab9:
    st.header("📊 Limites e Uso (Grist)")
    st.info("""
    💡 **Métricas Reais:** 
    - **Dados (10MB):** Calculado via tamanho real do arquivo SQLite (sem histórico).
    - **Densidade (Células):** Útil para saber qual tabela específica está 'pesada'.
    """)
    
    # 1. Fetch all documents
    if st.session_state.mapped_data is not None:
        all_docs_list = st.session_state.mapped_data[['Documento', 'Doc ID', 'Workspace']].drop_duplicates()
    else:
        with st.spinner("Buscando lista de documentos..."):
            workspaces = get_workspaces_and_docs(CURRENT_BASE_URL, selected_org_id)
            all_docs = []
            for ws in workspaces:
                for doc in ws.get('docs', []):
                    all_docs.append({'Documento': doc['name'], 'Doc ID': doc['id'], 'Workspace': ws.get('name')})
            all_docs_list = pd.DataFrame(all_docs)

    if all_docs_list.empty:
        st.warning("Nenhum documento encontrado.")
    else:
        st.subheader("📋 Visão Geral de Limites (Todos os Documentos)")
        
        c_btn1, c_btn2 = st.columns(2)
        
        # Method A: Org API (Fast but might fail)
        if c_btn1.button("🚀 Relatório Consolidado (Rápido)", key="load_global_usage_btn", use_container_width=True):
            with st.spinner("Solicitando relatório da organização..."):
                org_usage_data = get_org_usage(CURRENT_BASE_URL, selected_org_id)
                if org_usage_data and 'docs' in org_usage_data:
                    usage_map = {d['id']: d for d in org_usage_data['docs']}
                    usage_results = []
                    for _, row in all_docs_list.iterrows():
                        u = usage_map.get(row['Doc ID'])
                        if u:
                            rows_t = u.get('rowCount', {}).get('total', 0)
                            rows_l = u.get('rowCount', {}).get('limit', 5000)
                            data_t = u.get('dataSize', {}).get('total', 0)
                            data_l = u.get('dataSize', {}).get('limit', 10*1024*1024)
                            att_t = u.get('attachmentsSize', {}).get('total', 0)
                            att_l = u.get('attachmentsSize', {}).get('limit', 1024*1024*1024)
                            usage_results.append({
                                'Documento': row['Documento'], 'Workspace': row['Workspace'],
                                'Linhas (%)': round((rows_t / rows_l * 100), 1) if rows_l > 0 else 0,
                                'Dados (%)': round((data_t / data_l * 100), 1) if data_l > 0 else 0,
                                'Anexos (%)': round((att_t / att_l * 100), 1) if att_l > 0 else 0,
                                'Total Linhas': rows_t, 'Aviso': '✅ OK'
                            })
                        else:
                            usage_results.append({'Documento': row['Documento'], 'Workspace': row['Workspace'], 'Linhas (%)': 0, 'Dados (%)': 0, 'Anexos (%)': 0, 'Total Linhas': 0, 'Aviso': '⚠️ Não listado'})
                    st.session_state.global_usage_df = pd.DataFrame(usage_results)
                else:
                    st.error("❌ Relatório consolidado indisponível para esta conta. Use o Modo Profundo.")

        # Method B: Parallel Iterative Scan (Slower but reliable)
        if c_btn2.button("🔍 Modo Profundo (Paralelo)", key="load_deep_usage_btn", use_container_width=True):
            usage_results = []
            status_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            def scan_single_doc(doc_row):
                d_id = doc_row['Doc ID']
                # 1. Get real file size (Data)
                real_size = get_real_data_size(CURRENT_BASE_URL, d_id)
                
                # 2. Try usage API for rows
                usage, status = get_doc_usage(CURRENT_BASE_URL, d_id)
                
                rows_t = 0
                if usage:
                    rows_t = usage.get('rowCount', {}).get('total', 0)
                    att_pct = round((usage.get('attachmentsSize', {}).get('total', 0) / usage.get('attachmentsSize', {}).get('limit', 1024*1024*1024) * 100), 1)
                else:
                    # Fallback row count
                    try:
                        tables = get_tables(CURRENT_BASE_URL, d_id)
                        for t in tables:
                            if not t['id'].startswith('_grist'):
                                rows_t += get_table_row_count(CURRENT_BASE_URL, d_id, t['id'])
                    except: pass
                    att_pct = 0.0

                return {
                    'Documento': doc_row['Documento'], 'Workspace': doc_row['Workspace'],
                    'Linhas (%)': round((rows_t / 5000 * 100), 1),
                    'Dados (%)': round((real_size / (10 * 1024 * 1024) * 100), 1),
                    'Anexos (%)': att_pct,
                    'Total Linhas': rows_t, 'Aviso': '✅ OK (Scan Direto)'
                }

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(scan_single_doc, row) for _, row in all_docs_list.iterrows()]
                for i, future in enumerate(futures):
                    usage_results.append(future.result())
                    progress_bar.progress((i + 1) / len(futures))
                    status_placeholder.text(f"Processando {i+1}/{len(futures)} documentos...")
            
            st.session_state.global_usage_df = pd.DataFrame(usage_results)
            status_placeholder.empty()
            progress_bar.empty()

        if 'global_usage_df' in st.session_state:
            st.dataframe(
                st.session_state.global_usage_df.sort_values(by='Linhas (%)', ascending=False),
                use_container_width=True, hide_index=True,
                column_config={
                    "Linhas (%)": st.column_config.ProgressColumn("Linhas (%)", format="%.1f%%", min_value=0, max_value=100),
                    "Dados (%)": st.column_config.ProgressColumn("Dados (%)", format="%.1f%%", min_value=0, max_value=100),
                    "Anexos (%)": st.column_config.ProgressColumn("Anexos (%)", format="%.1f%%", min_value=0, max_value=100),
                }
            )

# --- TAB 10: Popular Tabelas ---
with tab10:
    st.header("📥 Popular Tabelas com IA")
    st.markdown("Gere templates para que um LLM (Gemini, ChatGPT) crie dados fictícios para suas tabelas.")

    if st.session_state.mapped_data is not None:
        all_docs_list = st.session_state.mapped_data[['Documento', 'Doc ID']].drop_duplicates()
        doc_opts_pop = {r['Documento']: r['Doc ID'] for _, r in all_docs_list.iterrows()}
    else:
        wss = get_workspaces_and_docs(CURRENT_BASE_URL, selected_org_id)
        doc_opts_pop = {d['name']: d['id'] for ws in wss for d in ws.get('docs', [])}
    
    sel_doc_pop_name = st.selectbox("1. Selecione o Documento", sorted(doc_opts_pop.keys()), index=None, key="pop_doc_sel")
    
    if sel_doc_pop_name:
        doc_id_pop = doc_opts_pop[sel_doc_pop_name]
        tables_pop = get_tables(CURRENT_BASE_URL, doc_id_pop)
        table_ids_pop = sorted([t['id'] for t in tables_pop if not t['id'].startswith('_grist')])
        
        sel_tables_pop = st.multiselect("2. Selecione as Tabelas para popular", table_ids_pop, key="pop_tables_sel")
        
        if sel_tables_pop:
            if st.button("🪄 Gerar Template para LLM"):
                template = []
                for t_id in sel_tables_pop:
                    cols = get_columns(CURRENT_BASE_URL, doc_id_pop, t_id)
                    col_info = {c['id']: c['fields'].get('type', 'Text') for c in cols if not c['fields'].get('isFormula')}
                    
                    table_template = {
                        "__METADATA__": {
                            "instrucao": f"Gere dados fictícios realistas para a tabela '{t_id}'.",
                            "tabela": t_id,
                            "colunas_e_tipos": col_info
                        },
                        "table_id": t_id,
                        "records": [
                            {cid: "..." for cid in col_info.keys()}
                        ]
                    }
                    template.append(table_template)
                
                st.session_state.pop_template_json = json.dumps(template, indent=2, ensure_ascii=False)
            
            if "pop_template_json" in st.session_state:
                st.markdown("### 📝 Template Gerado")
                st.caption("Copie o JSON abaixo e peça ao LLM para preencher a lista 'records'.")
                st.text_area("Template para o LLM", value=st.session_state.pop_template_json, height=300, key="pop_template_area")
                
                st.divider()
                st.markdown("### 📥 Importar Dados da IA")
                pop_input_json = st.text_area("Cole aqui o JSON preenchido pela IA:", height=300, key="pop_input_area")
                
                if st.button("🚀 Executar Povoamento", type="primary"):
                    if not pop_input_json.strip():
                        st.error("JSON de entrada vazio.")
                    else:
                        try:
                            import_data = json.loads(pop_input_json)
                            if not isinstance(import_data, list):
                                import_data = [import_data]
                            
                            with st.status("Processando inserção de dados...", expanded=True) as status_pop:
                                for item in import_data:
                                    t_id = item.get("table_id")
                                    records = item.get("records", [])
                                    
                                    if t_id and records:
                                        # Filtrar metadados se o LLM os manteve nos records (improvável mas por segurança)
                                        clean_records = []
                                        for r in records:
                                            clean_r = {k: v for k, v in r.items() if not k.startswith("__")}
                                            clean_records.append(clean_r)
                                        
                                        status_pop.write(f"📥 Inserindo {len(clean_records)} registros em **{t_id}**...")
                                        ok, msg = add_records(CURRENT_BASE_URL, doc_id_pop, t_id, clean_records)
                                        if ok:
                                            status_pop.write(f"✅ {t_id}: {msg}")
                                        else:
                                            status_pop.write(f"❌ {t_id}: {msg}")
                                status_pop.update(label="Povoamento Concluído!", state="complete")
                                st.balloons()
                        except Exception as e:
                            st.error(f"Erro ao processar JSON: {e}")
    else:
        st.info("Selecione um documento para começar.")


        