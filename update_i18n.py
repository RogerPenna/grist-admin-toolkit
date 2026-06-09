import re

i18n_additions = {
    'pt': {
        'err_fetch_orgs': 'Erro ao buscar organizações: {e}',
        'err_fetch_org_users': 'Erro ao buscar usuários da organização: {e}',
        'err_fetch_workspaces': 'Erro ao buscar workspaces: {e}',
        'err_fetch_tables': 'Erro ao buscar tabelas: {e}',
        'err_fetch_rules': 'Erro ao buscar regras: {e}',
        'btn_clone': '🚀 Clonar',
        'toast_completed': 'Concluído!',
        'header_transporter': '🚚 Transportador de Dados',
        't_dest_doc': 'Doc Destino',
        'console_operations': '### 📝 Console de Operações',
        'inspector_debug': '🔍 Inspetor de Dados (Debug)',
        'inspector_desc': 'Visualize os dados brutos de qualquer tabela (incluindo colunas escondidas) e exporte para análise.',
        'err_read_hidden_schema': 'Erro ao ler esquema oculto: {e}',
        'err_records': 'Erro nos registros: {err_i}',
        'col_metadata': '📋 Metadados das Colunas (Schema)',
        'json_schema': '**JSON do Schema (Debug):**',
        'raw_records': '📄 Registros Brutos',
        'x_rows_selected': '👉 **{count} linhas selecionadas.**',
        'json_data': '**JSON dos Dados (Debug):**',
        'header_audit': '⚖️ Auditoria de Integridade',
        'load_config': 'Carregar Config',
        'new_config': '(Nova)',
        'target_doc': 'Doc Alvo',
        'ref_table': 'Tabela Ref',
        'btn_audit': '🔎 Auditoria',
        'btn_grant': '✨ Conceder',
        'btn_remove': '🗑️ Remover',
        'header_blueprint': '🛠️ Blueprint (JSON)',
        'new_doc_section': '1. Novo Doc',
        'btn_create': '🆕 Criar',
        'success_created': 'Criado! {res}',
        'apply_structure_section': '2. Aplicar Estrutura',
        'overwrite_warning': '🔥 Sobrescrita (Apagará todas as tabelas atuais)',
        'blueprint_json': 'Blueprint JSON',
        'warning_mod_doc': '⚠️ **Atenção:** Você está prestes a modificar o documento **{target_b}** no servidor **{CURRENT_BASE_URL}**.',
        'confirm_exec_checkbox': 'Eu confirmo que o documento alvo e o servidor estão corretos.',
        'btn_exec': '🚀 Executar',
        'err_empty_json_overwrite': 'JSON vazio. Marque \'Sobrescrita\' se deseja apenas limpar o documento.',
        'info_disable_formulas': 'Desativando fórmulas para evitar erros de dependência no servidor...',
        'err_clean_doc': 'Erro ao limpar documento: {m_del}',
        'success_clean_doc': '🧹 Limpeza concluída: {count} tabelas removidas.',
        'info_no_user_tables_clean': '🧹 Nenhuma tabela de usuário encontrada para limpar.',
        'success_clean_only': 'Operação concluída (Apenas limpeza).',
        'success_blueprint': 'Blueprint OK!',
        'err_generic': 'Erro: {e}',
        'header_ai': '📥 Popular com IA',
        'btn_gen_template': '🪄 Gerar Template',
        'btn_scan_limits': '🔍 Escanear Limites',
        'header_help': '📘 Ajuda',
        'help_markdown': '### 🔐 Gestão de Acessos\n- **Visão Global:** Usuários do Team Site.\n- **Mapeamento:** Auditoria em massa de quem acessa o quê.\n- **Ações Rápidas:** Convites e revogações expressas.\n\n### 🏗️ Engenharia de Dados\n- **Clonador:** Copia esqueletos de tabelas.\n- **Transportador:** Move dados entre documentos.\n- **Auditoria:** Cruza dados de tabelas com acessos reais.\n- **Blueprint:** Infraestrutura como código (JSON).',
        'warn_no_org': 'Nenhuma org.',
        'warn_key_needed': 'Chave necessária.',
        'msg_ok': 'OK!',
        'sidebar_lang': 'Language / Idioma',
        'lbl_tables': 'Tabelas',
        'lbl_ai_template': 'Template IA',
        'lbl_paste_ai': 'Cole Resposta IA',
        'btn_populate': '🚀 Povoar',
    },
    'en': {
        'err_fetch_orgs': 'Error fetching organizations: {e}',
        'err_fetch_org_users': 'Error fetching organization users: {e}',
        'err_fetch_workspaces': 'Error fetching workspaces: {e}',
        'err_fetch_tables': 'Error fetching tables: {e}',
        'err_fetch_rules': 'Error fetching rules: {e}',
        'btn_clone': '🚀 Clone',
        'toast_completed': 'Completed!',
        'header_transporter': '🚚 Data Transporter',
        't_dest_doc': 'Target Doc',
        'console_operations': '### 📝 Operations Console',
        'inspector_debug': '🔍 Data Inspector (Debug)',
        'inspector_desc': 'View raw data of any table (including hidden columns) and export for analysis.',
        'err_read_hidden_schema': 'Error reading hidden schema: {e}',
        'err_records': 'Error in records: {err_i}',
        'col_metadata': '📋 Column Metadata (Schema)',
        'json_schema': '**Schema JSON (Debug):**',
        'raw_records': '📄 Raw Records',
        'x_rows_selected': '👉 **{count} rows selected.**',
        'json_data': '**Data JSON (Debug):**',
        'header_audit': '⚖️ Integrity Audit',
        'load_config': 'Load Config',
        'new_config': '(New)',
        'target_doc': 'Target Doc',
        'ref_table': 'Ref Table',
        'btn_audit': '🔎 Audit',
        'btn_grant': '✨ Grant',
        'btn_remove': '🗑️ Remove',
        'header_blueprint': '🛠️ Blueprint (JSON)',
        'new_doc_section': '1. New Doc',
        'btn_create': '🆕 Create',
        'success_created': 'Created! {res}',
        'apply_structure_section': '2. Apply Structure',
        'overwrite_warning': '🔥 Overwrite (Will delete all current tables)',
        'blueprint_json': 'Blueprint JSON',
        'warning_mod_doc': '⚠️ **Warning:** You are about to modify the document **{target_b}** on server **{CURRENT_BASE_URL}**.',
        'confirm_exec_checkbox': 'I confirm the target document and server are correct.',
        'btn_exec': '🚀 Execute',
        'err_empty_json_overwrite': 'Empty JSON. Check \'Overwrite\' if you only want to clear the document.',
        'info_disable_formulas': 'Disabling formulas to prevent dependency errors on the server...',
        'err_clean_doc': 'Error clearing document: {m_del}',
        'success_clean_doc': '🧹 Cleanup completed: {count} tables removed.',
        'info_no_user_tables_clean': '🧹 No user tables found to clear.',
        'success_clean_only': 'Operation completed (Cleanup only).',
        'success_blueprint': 'Blueprint OK!',
        'err_generic': 'Error: {e}',
        'header_ai': '📥 Populate with AI',
        'btn_gen_template': '🪄 Generate Template',
        'btn_scan_limits': '🔍 Scan Limits',
        'header_help': '📘 Help',
        'help_markdown': '### 🔐 Access Management\n- **Global View:** Team Site users.\n- **Mapping:** Mass audit of who accesses what.\n- **Quick Actions:** Express invitations and revocations.\n\n### 🏗️ Data Engineering\n- **Cloner:** Copies table skeletons.\n- **Transporter:** Moves data between documents.\n- **Audit:** Crosses table data with real accesses.\n- **Blueprint:** Infrastructure as code (JSON).',
        'warn_no_org': 'No org.',
        'warn_key_needed': 'Key required.',
        'msg_ok': 'OK!',
        'sidebar_lang': 'Language / Idioma',
        'lbl_tables': 'Tables',
        'lbl_ai_template': 'AI Template',
        'lbl_paste_ai': 'Paste AI Response',
        'btn_populate': '🚀 Populate',
    }
}

with open("grist_admin_toolkit.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find the i18n dictionary and update it
pt_match = re.search(r"('pt': \{)(.*?)(    \},)", content, re.DOTALL)
en_match = re.search(r"('en': \{)(.*?)(    \}\n\})", content, re.DOTALL)

if pt_match and en_match:
    pt_block = pt_match.group(2)
    en_block = en_match.group(2)
    
    new_pt_entries = ""
    for k, v in i18n_additions['pt'].items():
        val = repr(v)
        new_pt_entries += f"        '{k}': {val},\n"
    
    new_en_entries = ""
    for k, v in i18n_additions['en'].items():
        val = repr(v)
        new_en_entries += f"        '{k}': {val},\n"
        
    new_pt_block = pt_block + new_pt_entries
    new_en_block = en_block + new_en_entries
    
    content = content.replace(pt_match.group(0), pt_match.group(1) + new_pt_block + pt_match.group(3))
    content = content.replace(en_match.group(0), en_match.group(1) + new_en_block + en_match.group(3))
    
    with open("grist_admin_toolkit.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("i18n updated successfully.")
else:
    print("Failed to find i18n blocks.")
