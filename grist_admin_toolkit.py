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

# i18n Configuration
i18n = {
    'pt': {
        'page_title': 'Grist Admin & Data Toolkit',
        'sidebar_version': '**Version: 1.2**',
        'sidebar_conn_header': '🔌 Conexão',
        'sidebar_server': 'Servidor',
        'sidebar_add_server': '+ Adicionar Novo Servidor...',
        'sidebar_new_url': 'Nova URL Base',
        'sidebar_api_key': 'Grist API Key',
        'sidebar_save_key': 'Salvar chave',
        'sidebar_connect_btn': 'Conectar / Atualizar',
        'sidebar_org': 'Organização',
        'sidebar_base_url': '📍 Base URL: {url}',
        'sidebar_reload_btn': '🔄 Recarga Geral',
        'sidebar_main_menu_header': '🧭 Menu Principal',
        'sidebar_go_to': 'Ir para:',
        'menu_access': '🔐 Gestão de Acessos',
        'menu_data': '🏗️ Engenharia de Dados',
        'menu_system': '⚙️ Sistema',
        'main_title': '🛠️ Grist Admin & Data Toolkit',
        
        # Tabs - Access
        'tab_global_view': '👥 Visão Global',
        'tab_mapping': '🗺️ Mapeamento',
        'tab_quick_actions': '⚡ Ações Rápidas',
        'tab_acl': '🛡️ Regras (ACL)',
        
        # Tabs - Data Engineering
        'tab_cloner': '🏗️ Clonador',
        'tab_transporter': '🚚 Transportador',
        'tab_import': '📥 Importador CSV/JSON',
        'tab_audit': '⚖️ Auditoria Integridade',
        'tab_blueprint': '🛠️ Blueprint',
        'tab_ai': '📥 IA',
        
        # Tabs - System
        'tab_limits': '📊 Limites',
        'tab_help': '❓ Ajuda',
        
        # Access -> Global View
        'header_users': 'Usuários: {org}',
        'filter_name': 'Filtrar Nome',
        'filter_email': 'Filtrar Email',
        'user_details': '🕵️ Detalhes por Usuário',
        'select_user': 'Selecione Usuário',
        'no_direct_access': 'Sem acessos diretos.',
        'do_mapping_tab2': 'Faça o mapeamento na aba 2.',
        
        # Access -> Mapping
        'header_doc_mapping': 'Mapeamento de Documentos',
        'btn_start_mapping': '🚀 Iniciar Mapeamento',
        'status_scanning': 'Varrendo...',
        'filters': '### 🔍 Filtros',
        'hide_inherited': 'Ocultar herdados',
        'doc': 'Doc',
        'email': 'Email',
        'name': 'Nome',
        'access': 'Acesso',
        'showing_x_of_y': 'Exibindo {x} de {y}',
        'btn_sel_all': '✅ Sel. Todos',
        'btn_clear_sel': '❌ Limpar Sel.',
        'operations': '📦 Operações ({count})',
        'dest_doc': 'Doc Destino',
        'btn_copy': '📄 Copiar',
        'toast_copy_ok': 'Cópia OK!',
        'new_level': 'Novo Nível',
        'btn_update': '✏️ Atualizar',
        'toast_updated': 'Atualizado!',
        'header_org_invite': '➕ Convidar para Organização',
        'emails_to_invite': 'Emails (Separados por vírgula ou espaço)',
        'btn_invite': '🚀 Convidar',
        'toast_invited': 'Convites enviados!',
        'warn_non_members': '⚠️ **Usuários Externos:** Os seguintes usuários não são membros da organização. Eles serão adicionados como **GUESTS** (limitado a 2 no plano free):',
        'btn_add_to_org_first': '🏢 Adicionar à Organização Primeiro',
        'btn_proceed_guest': '👤 Prosseguir como Guest',
        'role_owners': 'Proprietário',
        'role_editors': 'Editor',
        'role_viewers': 'Observador',
        'role_members': 'Membro (Sem Acesso Padrão)',
        
        # Access -> Quick Actions
        'header_quick_actions': '⚡ Ações Rápidas',
        'select_doc': 'Selecionar Doc',
        'emails_add': 'Emails (Adicionar)',
        'level': 'Nível',
        'btn_add': 'Adicionar',
        'toast_added': 'Adicionados!',
        'emails_remove': 'Emails (Remover)',
        'btn_remove': 'Remover',
        'toast_removed': 'Removidos!',
        'mapping_needed': 'Mapeamento necessário.',
        
        # Access -> ACL
        'header_acl': '🛡️ Regras de Acesso (ACL)',
        'doc_audit': 'Doc para Auditoria',
        'tab_view': '👁️ Visualizar',
        'tab_edit': '✍️ Editar',
        'btn_load': '🔍 Carregar',
        'new_json_rules': 'Novo JSON de Regras',
        'btn_apply': '📤 Aplicar',
        'btn_gen_json': '🪄 Gerar JSON (para IA)',
        'toast_applied': 'Aplicado!',
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
        'err_empty_json_overwrite': "JSON vazio. Marque 'Sobrescrita' se deseja apenas limpar o documento.",
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
        'help_markdown': '<div id="help-top"></div>\n\n# 📖 Guia Completo do Usuário\n\nBem-vindo ao **Grist Admin & Data Toolkit**. Esta aplicação foi desenhada para usuários avançados e administradores gerenciarem organizações complexas no Grist, auditarem segurança em escala e realizarem tarefas avançadas de engenharia de dados.\n\n<a name="sidebar"></a>\n## 🧭 Barra Lateral & Navegação\nA barra lateral é seu centro de comando. \n- **Conexão:** Você pode se conectar ao Grist SaaS padrão (`docs.getgrist.com`) ou qualquer instância auto-hospedada.\n- **Chave API:** Requer uma chave API válida com permissões de **Owner**.\n- **Organização:** Alternar a organização atualiza o escopo de todas as abas.\n- **Recarga Total:** Limpa o cache local e força uma nova busca no servidor.\n\n---\n\n# 🔐 Gestão de Acessos\n\n### 👥 Visão Global\nEsta aba mostra usuários que são membros do **Team Site** (nível da Organização).\n- **Lista de Usuários:** Exibe o email principal, nome de exibição e seu papel global (Viewer, Editor, Admin).\n- **Detalhes do Usuário (Auditoria Profunda):** Se você realizou um scan na aba de **Mapeamento**, pode selecionar um usuário aqui para ver cada documento individual ao qual ele tem acesso **direto**.\n\n### 🗺️ Mapeamento de Documentos\nO motor de Mapeamento realiza uma auditoria de segurança recursiva.\n- **Escaneamento:** Como envolve muitas chamadas de API, pode levar alguns minutos em organizações grandes.\n- **Cache:** Resultados são salvos em `mapping_cache.json`.\n- **Filtros:** Use o filtro "Ocultar Herdados" para ver apenas permissões concedidas explicitamente no nível do documento.\n\n### 🛡️ Regras de Acesso (ACL)\nAs tabelas internas do Grist (`_grist_ACLRules` e `_grist_ACLResources`) são notoriamente difíceis de ler. Esta ferramenta as **denormaliza** em uma grade legível.\n- **Edição Assistida por IA:** Use o botão **"🪄 Gerar JSON (para IA)"** para exportar as regras atuais e modificá-las com a ajuda de uma IA.\n\n# 🏗️ Engenharia de Dados\n\n### 🚚 Transportador de Dados\nMove conjuntos de dados entre documentos preservando relações e fórmulas em 3 fases (Estrutura, Dados e Inteligência).\n\n### 🛠️ Blueprint (JSON)\nInfraestrutura como Código para o Grist.\n- **Extração com IA:** Use o botão **"🪄 Gerar JSON (para IA)"** para capturar a estrutura de um documento existente.\n\n### 📥 Popular com IA\nIntegração para gerar dados de teste realistas.\n- **Templates Melhorados:** Agora inclui **exemplos reais** das suas tabelas para dar contexto à IA.',
        'warn_no_org': 'Nenhuma org.',
        'warn_key_needed': 'Chave necessária.',
        'msg_ok': 'OK!',
        'sidebar_lang': 'Language / Idioma',
        'lbl_tables': 'Tabelas',
        'lbl_ai_template': 'Template IA',
        'lbl_paste_ai': 'Cole Resposta IA',
        'btn_populate': '🚀 Povoar',
        'doc_source': 'Doc Origem',
        'doc_to_inspect': 'Documento para Inspecionar',
        'doc_name': 'Nome Doc',
        'btn_inspect_all': '🔍 Inspecionar Tudo',
        'lbl_workspace': 'Workspace',
        'lbl_table': 'Tabela',
        'newly_created': '✨ Recém Criado',
        'lbl_targets': 'Destinos',
        'lbl_tables_to_transport': 'Tabelas para Transportar',
        'lbl_col_title': 'Coluna Título',
        'lbl_col_email': 'Colunas Email',
        'btn_phase1': '1️⃣ Executar Fase 1 (Estrutura)',
        'btn_phase2': '2️⃣ Executar Fase 2 (Dados)',
        'btn_phase3': '3️⃣ Executar Fase 3 (Fórmulas)',
    },
    'en': {
        'page_title': 'Grist Admin & Data Toolkit',
        'sidebar_version': '**Version: 1.2**',
        'sidebar_conn_header': '🔌 Connection',
        'sidebar_server': 'Server',
        'sidebar_add_server': '+ Add New Server...',
        'sidebar_new_url': 'New Base URL',
        'sidebar_api_key': 'Grist API Key',
        'sidebar_save_key': 'Save key',
        'sidebar_connect_btn': 'Connect / Update',
        'sidebar_org': 'Organization',
        'sidebar_base_url': '📍 Base URL: {url}',
        'sidebar_reload_btn': '🔄 Full Reload',
        'sidebar_main_menu_header': '🧭 Main Menu',
        'sidebar_go_to': 'Go to:',
        'menu_access': '🔐 Access Management',
        'menu_data': '🏗️ Data Engineering',
        'menu_system': '⚙️ System',
        'main_title': '🛠️ Grist Admin & Data Toolkit',
        
        # Tabs - Access
        'tab_global_view': '👥 Global View',
        'tab_mapping': '🗺️ Mapping',
        'tab_quick_actions': '⚡ Quick Actions',
        'tab_acl': '🛡️ Rules (ACL)',
        
        # Tabs - Data Engineering
        'tab_cloner': '🏗️ Cloner',
        'tab_transporter': '🚚 Transporter',
        'tab_import': '📥 CSV/JSON Importer',
        'tab_audit': '⚖️ Integrity Audit',
        'tab_blueprint': '🛠️ Blueprint',
        'tab_ai': '📥 AI',
        
        # Tabs - System
        'tab_limits': '📊 Limits',
        'tab_help': '❓ Help',
        
        # Access -> Global View
        'header_users': 'Users: {org}',
        'filter_name': 'Filter Name',
        'filter_email': 'Filter Email',
        'user_details': '🕵️ Details by User',
        'select_user': 'Select User',
        'no_direct_access': 'No direct access.',
        'do_mapping_tab2': 'Perform mapping in tab 2.',
        
        # Access -> Mapping
        'header_doc_mapping': 'Document Mapping',
        'btn_start_mapping': '🚀 Start Mapping',
        'status_scanning': 'Scanning...',
        'filters': '### 🔍 Filters',
        'hide_inherited': 'Hide inherited',
        'doc': 'Doc',
        'email': 'Email',
        'name': 'Name',
        'access': 'Access',
        'showing_x_of_y': 'Showing {x} of {y}',
        'btn_sel_all': '✅ Sel. All',
        'btn_clear_sel': '❌ Clear Sel.',
        'operations': '📦 Operations ({count})',
        'dest_doc': 'Target Doc',
        'btn_copy': '📄 Copy',
        'toast_copy_ok': 'Copy OK!',
        'new_level': 'New Level',
        'btn_update': '✏️ Update',
        'toast_updated': 'Updated!',
        'header_org_invite': '➕ Invite to Organization',
        'emails_to_invite': 'Emails (Comma or space separated)',
        'btn_invite': '🚀 Invite',
        'toast_invited': 'Invitations sent!',
        'warn_non_members': '⚠️ **External Users:** The following users are not members of the organization. They will be added as **GUESTS** (limited to 2 on free plan):',
        'btn_add_to_org_first': '🏢 Add to Organization First',
        'btn_proceed_guest': '👤 Proceed as Guest',
        'role_owners': 'Owner',
        'role_editors': 'Editor',
        'role_viewers': 'Viewer',
        'role_members': 'Member (No Default Access)',
        
        # Access -> Quick Actions
        'header_quick_actions': '⚡ Quick Actions',
        'select_doc': 'Select Doc',
        'emails_add': 'Emails (Add)',
        'level': 'Level',
        'btn_add': 'Add',
        'toast_added': 'Added!',
        'emails_remove': 'Emails (Remove)',
        'btn_remove': 'Remove',
        'toast_removed': 'Removed!',
        'mapping_needed': 'Mapping needed.',
        
        # Access -> ACL
        'header_acl': '🛡️ Access Rules (ACL)',
        'doc_audit': 'Doc for Audit',
        'tab_view': '👁️ View',
        'tab_edit': '✍️ Edit',
        'btn_load': '🔍 Load',
        'new_json_rules': 'New Rules JSON',
        'btn_apply': '📤 Apply',
        'btn_gen_json': '🪄 Generate JSON (for AI)',
        'toast_applied': 'Applied!',
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
        'err_empty_json_overwrite': "Empty JSON. Check 'Overwrite' if you only want to clear the document.",
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
        'header_help': '❓ Help',
        'help_markdown': '<div id="help-top"></div>\n\n# 📖 Comprehensive User Guide\n\nWelcome to the **Grist Admin & Data Toolkit**. This application is designed for power users and administrators to manage complex Grist organizations, audit security at scale, and perform advanced data engineering tasks.\n\n<a name="sidebar"></a>\n## 🧭 Sidebar & Navigation\nThe sidebar is your command center. \n- **Connection:** You can connect to the standard Grist SaaS (`docs.getgrist.com`) or any self-hosted instance. When adding a custom server, provide the full API URL (e.g., `https://grist.example.com/api`).\n- **API Key:** Requires a valid API Key with **Owner** permissions for the tasks you intend to perform.\n- **Organization:** Switching the organization updates the scope of all tabs. Most tools will only "see" documents within the selected organization.\n- **Full Reload:** Clears the local cache and forces a fresh fetch of organizations and workspaces from the server.\n\n---\n\n# 🔐 Access Management\n\n<a name="global-view"></a>\n### 👥 Global View\nThis tab shows users who are members of the **Team Site** (Organization level).\n- **User List:** Displays the primary email, display name, and their organization-wide role (Viewer, Editor, Admin).\n- **User Details (Deep Audit):** If you have performed a scan in the **Mapping** tab, you can select a user here to see every individual document they have **direct** access to. This is essential for identifying "permission creep" where a user has more access than their global role suggests.\n\n<a name="mapping"></a>\n### 🗺️ Document Mapping\nThe Mapping engine performs a recursive security audit. It iterates through every workspace and every document in the organization, calling the Grist Access API for each.\n- **Scanning:** Since this involves many API calls, it can take a few minutes for large organizations. \n- **Cache:** Results are stored in `mapping_cache.json` to allow you to work across sessions without re-scanning.\n- **Filtering:** Use the filters to find specific users or documents. The "Hide Inherited" option is crucial—it filters out users who have access simply because they are part of a workspace, showing you only those with explicitly granted document-level permissions.\n- **Bulk Operations:** Select multiple users/documents and use the **Operations** panel to:\n    - **Copy Permissions:** Replicate a set of users and their roles from one document to another.\n    - **Update Roles:** Change the access level (e.g., Viewer to Editor) for all selected rows at once.\n\n<a name="quick-actions"></a>\n### ⚡ Quick Actions\nDesigned for speed. If you have a list of 50 emails that need to be added to a specific project document immediately, this is the tool.\n- **Add/Remove:** Paste a list of emails (comma, space, or newline separated). The tool will normalize the emails (lowercase, trim) and apply the requested role.\n\n<a name="acl"></a>\n### 🛡️ Access Rules (ACL)\nGrist\'s internal `_grist_ACLRules` and `_grist_ACLResources` tables are notoriously difficult to read. This tool **denormalizes** them into a human-readable grid.\n- **View:** See which tables and columns are protected and by what formula.\n- **Edit:** For advanced users, you can paste a JSON structure to completely redefine the rules. \n- **AI-Assisted Editing:** Use the **"🪄 Generate JSON (for AI)"** button to export the current rules. Paste this into an AI (like ChatGPT or Gemini), ask for modifications, and paste the result back to apply.\n- **Safety:** Every time you apply new rules, the tool automatically saves a timestamped JSON backup in the `/backups` folder. If you break the Sandbox, you can restore from these files.\n\n---\n\n# 🏗️ Data Engineering\n\n<a name="cloner"></a>\n### 🏗️ Table Cloner\nCopies the **Schema** (structure) of a table from a source document to one or more target documents.\n- It copies column IDs, Labels, Types, Formulas, and Widget Options.\n- **Note:** It does **not** move the data (rows), only the structure. Ideal for creating templates.\n\n<a name="transporter"></a>\n### 🚚 Data Transporter\nA sophisticated 3-phase engine to move entire datasets between documents while preserving relationships and formulas.\n- **Phase 1 (Structure):** Creates the tables. To prevent "Sandbox Errors" caused by circular references (e.g., Table A refers to B, and B refers to A), it initially creates all Reference columns as "Any" type.\n- **Phase 2 (Data):** Transfers all records in batches of 500. Reference IDs (Row IDs) are preserved.\n- **Phase 3 (Formulas):** The "Intelligence" phase. It updates the columns to their final types, restores the `visibleCol` mapping (the column shown in the dropdown), and re-activates Python formulas.\n\n<a name="audit"></a>\n### ⚖️ Integrity Audit\nThis is a specialized "Sync" tool. It compares a **Control Table** (a table inside Grist where you manage who *should* have access) with **Actual Grist Permissions**.\n- **Missing (🔴):** Users who are in your table but don\'t actually have access to the document. Use "Grant" to fix this.\n- **Orphan (☢️):** Users who have access to the document but are NOT in your control table. Use "Remove" to revoke unauthorized access.\n\n<a name="blueprint"></a>\n### 🛠️ Blueprint (JSON)\nEnables "Infrastructure as Code" for Grist.\n- **AI Blueprinting:** Use the **"🪄 Generate JSON (for AI)"** button to capture the structure of an existing document. This is perfect for refactoring or cloning structures with AI help.\n- **Wipe & Rebuild:** If "Overwrite" is checked, the tool performs a **"Lobotomy"**: it first converts all columns in the document to plain text (removing formulas) to ensure the Grist Sandbox doesn\'t crash during table deletion. It then deletes all tables and rebuilds the document from your JSON blueprint.\n\n<a name="ai"></a>\n### 📥 Populate with AI\nBridge the gap between LLMs and Grist.\n- **Enhanced Templates:** The template generated now includes **real sample records** from your tables. This provides the AI with crucial context on your data format, leading to much better generation results.\n- **Workflow:** Paste this template into ChatGPT/Claude with a prompt like "Fill this with 20 realistic rows of project data". Paste the AI response back into the tool to populate your table instantly.\n\n---\n\n# ⚙️ System\n\n<a name="limits"></a>\n### 📊 Limits & Usage\nGrist documents perform best when kept under certain row counts and file sizes.\n- **Scan Limits:** Calculates usage percentages for every document in the organization.\n- **Linhas (%):** Based on the standard 5,000 row "soft limit" for optimal performance.\n- **Dados (%):** Based on a 10MB SQLite file size limit. Helps you identify docs that need optimization or history clearing.',
        'warn_no_org': 'No org.',
        'warn_key_needed': 'Key required.',
        'msg_ok': 'OK!',
        'sidebar_lang': 'Language / Idioma',
        'lbl_tables': 'Tables',
        'lbl_ai_template': 'AI Template',
        'lbl_paste_ai': 'Paste AI Response',
        'btn_populate': '🚀 Populate',
        'doc_source': 'Source Doc',
        'doc_to_inspect': 'Document to Inspect',
        'doc_name': 'Doc Name',
        'btn_inspect_all': '🔍 Inspect All',
        'lbl_workspace': 'Workspace',
        'lbl_table': 'Table',
        'newly_created': '✨ Newly Created',
        'lbl_targets': 'Targets',
        'lbl_tables_to_transport': 'Tables to Transport',
        'lbl_col_title': 'Title Column',
        'lbl_col_email': 'Email Columns',
        'btn_phase1': '1️⃣ Execute Phase 1 (Structure)',
        'btn_phase2': '2️⃣ Execute Phase 2 (Data)',
        'btn_phase3': '3️⃣ Execute Phase 3 (Formulas)',
    }
}

# Page Configuration
st.set_page_config(
    page_title="Grist Admin & Data Toolkit",
    page_icon="🛠️",
    layout="wide"
)

if 'lang' not in st.session_state:
    st.session_state.lang = 'en'

# 1. Configuration & Setup
load_dotenv()

# Persistence for custom servers
SAVED_SERVERS_FILE = "saved_servers.json"

def load_saved_servers():
    """Loads a dict of {url: api_key}."""
    if os.path.exists(SAVED_SERVERS_FILE):
        try:
            with open(SAVED_SERVERS_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list): # Migration from old format
                    return {url: "" for url in data}
                return data
        except:
            return {}
    return {}

def save_server(url, api_key=""):
    if not url or url == "https://docs.getgrist.com/api":
        return
    servers = load_saved_servers()
    servers[url] = api_key
    with open(SAVED_SERVERS_FILE, "w") as f:
        json.dump(servers, f, indent=2)

def delete_server(url):
    servers = load_saved_servers()
    if url in servers:
        del servers[url]
        with open(SAVED_SERVERS_FILE, "w") as f:
            json.dump(servers, f, indent=2)

def get_auth_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest"
    }

# Helper: Email Normalization
def normalize_email(email_str):
    if not email_str: return ""
    email_str = email_str.strip().lower()
    nks = unicodedata.normalize('NFKD', email_str)
    sanitized = "".join([c for c in nks if not unicodedata.combining(c)])
    sanitized = re.sub(r'[^a-z0-9@._\-\+]', '', sanitized)
    return sanitized

# 2. API Helper Functions with Caching

@st.cache_data(ttl=300)
def get_orgs(base_url, api_key):
    """Fetches available organizations."""
    base_url = base_url.strip().rstrip("/")
    try:
        response = requests.get(f"{base_url}/orgs", headers=get_auth_headers(api_key))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(i18n[st.session_state.lang]["err_fetch_orgs"].format(e=e))
        return []

@st.cache_data(ttl=300)
def get_org_users(base_url, api_key, org_id):
    """Fetches users at the organization level."""
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/orgs/{org_id}/access"
        response = requests.get(url, headers=get_auth_headers(api_key))
        response.raise_for_status()
        data = response.json()
        return data.get("users", [])
    except Exception as e:
        st.error(i18n[st.session_state.lang]["err_fetch_org_users"].format(e=e))
        return []

@st.cache_data(ttl=300)
def get_workspaces_and_docs(base_url, api_key, org_id):
    """Fetches all workspaces and their documents for an org."""
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/orgs/{org_id}/workspaces"
        response = requests.get(url, headers=get_auth_headers(api_key))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(i18n[st.session_state.lang]["err_fetch_workspaces"].format(e=e))
        return []

@st.cache_data(ttl=600)
def get_doc_users(base_url, api_key, doc_id):
    """Fetches users assigned to a specific document."""
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/docs/{doc_id}/access"
        response = requests.get(url, headers=get_auth_headers(api_key))
        response.raise_for_status()
        data = response.json()
        return data.get("users", [])
    except Exception as e:
        return []

def update_doc_access(base_url, api_key, doc_id, email, role):
    """Updates user access via PATCH /access with delta."""
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/docs/{doc_id.strip()}/access"
        payload = {"delta": {"users": {email.strip(): role}}}
        response = requests.patch(url, headers=get_auth_headers(api_key), json=payload)
        if response.status_code != 200:
             return False, f"Erro {response.status_code}: {response.text}"
        return True, "Sucesso!"
    except Exception as e:
        return False, str(e)

def update_org_access(base_url, api_key, org_id, email, role):
    """Updates user access at the organization level via PATCH /access with delta."""
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/orgs/{org_id}/access"
        payload = {"delta": {"users": {email.strip(): role}}}
        response = requests.patch(url, headers=get_auth_headers(api_key), json=payload)
        if response.status_code != 200:
             return False, f"Erro {response.status_code}: {response.text}"
        return True, "Sucesso!"
    except Exception as e:
        return False, str(e)

@st.cache_data(ttl=300)
def get_tables(base_url, api_key, doc_id):
    """Fetches list of tables for a document."""
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/docs/{doc_id}/tables"
        response = requests.get(url, headers=get_auth_headers(api_key))
        response.raise_for_status()
        return response.json().get('tables', [])
    except Exception as e:
        st.error(i18n[st.session_state.lang]["err_fetch_tables"].format(e=e))
        return []

def get_tables_no_cache(base_url, api_key, doc_id):
    """Fetches list of tables for a document without caching."""
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/docs/{doc_id}/tables"
        response = requests.get(url, headers=get_auth_headers(api_key))
        response.raise_for_status()
        return response.json().get('tables', [])
    except Exception as e:
        return []

@st.cache_data(ttl=300)
def get_doc_usage(base_url, api_key, doc_id):
    """Fetches usage statistics for a document. Returns (data, status_code)."""
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/docs/{doc_id}/usage"
        response = requests.get(url, headers=get_auth_headers(api_key))
        if response.status_code == 200:
            return response.json(), 200
        return None, response.status_code
    except Exception:
        return None, 500

@st.cache_data(ttl=300)
def get_org_usage(base_url, api_key, org_id):
    """Fetches usage for all documents in an organization in a single call."""
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/orgs/{org_id}/usage"
        response = requests.get(url, headers=get_auth_headers(api_key))
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

@st.cache_data(ttl=300)
def get_table_row_count(base_url, api_key, doc_id, table_id):
    """Fetches row count for a specific table using SQL API."""
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/docs/{doc_id}/sql?q=SELECT COUNT(*) as count FROM {table_id}"
        response = requests.get(url, headers=get_auth_headers(api_key))
        if response.status_code == 200:
            records = response.json().get('records', [])
            if records:
                return records[0].get('fields', {}).get('count', 0)
        return 0
    except Exception:
        return 0

@st.cache_data(ttl=300)
def get_real_data_size(base_url, api_key, doc_id):
    """Fetches the actual SQLite file size (no history) using HEAD request on download endpoint."""
    try:
        url = f"{base_url}/docs/{doc_id}/download?nohistory=true"
        with requests.get(url, headers=get_auth_headers(api_key), stream=True) as r:
            if r.status_code == 200:
                size = r.headers.get('Content-Length')
                return int(size) if size else 0
        return 0
    except Exception:
        return 0

@st.cache_data(ttl=300)
def get_columns(base_url, api_key, doc_id, table_id):
    """Fetches columns for a specific table."""
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/docs/{doc_id}/tables/{table_id}/columns"
        response = requests.get(url, headers=get_auth_headers(api_key))
        response.raise_for_status()
        return response.json().get('columns', [])
    except Exception as e:
        return []

def get_columns_no_cache(base_url, api_key, doc_id, table_id):
    """Fetches columns for a specific table without caching."""
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/docs/{doc_id}/tables/{table_id}/columns"
        response = requests.get(url, headers=get_auth_headers(api_key))
        response.raise_for_status()
        return response.json().get('columns', [])
    except Exception as e:
        return []

def fetch_table_records(base_url, api_key, doc_id, table_name):
    """Fetches all records from a table. Returns (records, error_msg)."""
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/docs/{doc_id}/tables/{table_name}/records"
        response = requests.get(url, headers=get_auth_headers(api_key))
        if response.status_code == 404:
            return [], None # Table doesn't exist
        if response.status_code == 403:
            return [], "Acesso negado (403). Verifique se você é OWNER do documento."
        response.raise_for_status()
        return response.json().get('records', []), None
    except Exception as e:
        return [], str(e)

def add_records(base_url, api_key, doc_id, table_id, records):
    """Adds multiple records to a table. If records contain 'id' keys, uses PUT with require block to preserve custom IDs."""
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/docs/{doc_id}/tables/{table_id}/records"
        has_custom_ids = False
        if records and isinstance(records[0], dict):
            has_custom_ids = any("id" in r for r in records)
            
        if has_custom_ids:
            put_records = []
            for r in records:
                rec_id = r.get("id")
                fields = r.get("fields", {})
                if rec_id is not None:
                    put_records.append({
                        "require": {"id": rec_id},
                        "fields": fields
                    })
                else:
                    put_records.append({
                        "fields": fields
                    })
            payload = {"records": put_records}
            response = requests.put(url, headers=get_auth_headers(api_key), json=payload)
        else:
            if records and isinstance(records[0], dict) and ("fields" in records[0] or "id" in records[0]):
                payload = {"records": records}
            else:
                payload = {"records": [{"fields": r} for r in records]}
            response = requests.post(url, headers=get_auth_headers(api_key), json=payload)
            
        if response.status_code == 200:
            return True, f"{len(records)} registros adicionados."
        return False, f"Erro {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def create_table(base_url, api_key, doc_id, table_id, columns_payload):
    """Creates a new table in the document with the provided columns."""
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/docs/{doc_id}/tables"
        payload = {"tables": [{"id": table_id, "columns": columns_payload}]}
        response = requests.post(url, headers=get_auth_headers(api_key), json=payload)
        if response.status_code == 200:
            created_id = response.json().get('tables', [])[0].get('id', table_id)
            return True, created_id
        if "already exists" in response.text.lower():
            return False, "EXISTING"
        return False, f"Erro {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def add_columns(base_url, api_key, doc_id, table_id, columns_payload):
    """Adds columns to an existing table."""
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/docs/{doc_id}/tables/{table_id}/columns"
        payload = {"columns": columns_payload}
        response = requests.post(url, headers=get_auth_headers(api_key), json=payload)
        if response.status_code == 200:
            return True, "Colunas adicionadas."
        return False, f"Erro {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def update_columns(base_url, api_key, doc_id, table_id, columns_payload):
    """Updates existing columns metadata via the low-level /apply endpoint using ModifyColumn actions."""
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/docs/{doc_id}/apply"
        
        # Convert standard column payload into a list of ModifyColumn actions
        # Payload format: {"id": "ColName", "fields": {"type": "...", ...}}
        actions = []
        for col in columns_payload:
            col_id = col['id']
            col_fields = col.get('fields', {})
            # Remove keys that might cause issues if they are null
            clean_fields = {k: v for k, v in col_fields.items() if v is not None}
            actions.append(["ModifyColumn", table_id, col_id, clean_fields])
            
        payload = actions # The /apply endpoint expects just the array of arrays
        
        response = requests.post(url, headers=get_auth_headers(api_key), json=payload)
        if response.status_code == 200:
            return True, "Ações aplicadas com sucesso."
        return False, f"Erro {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def delete_tables_batch(base_url, api_key, doc_id, table_ids):
    if not table_ids: return True, "Nenhuma tabela."
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/docs/{doc_id}/apply"
        payload = [["RemoveTable", t_id] for t_id in table_ids]
        response = requests.post(url, headers=get_auth_headers(api_key), json=payload)
        if response.status_code == 200:
            return True, f"{len(table_ids)} tabelas removidas."
        return False, f"Erro {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def create_document(base_url, api_key, workspace_id, doc_name):
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/workspaces/{workspace_id}/docs"
        payload = {"name": doc_name}
        response = requests.post(url, headers=get_auth_headers(api_key), json=payload)
        if response.status_code == 200:
            return True, response.json()
        return False, f"Erro {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def load_audit_configs():
    if os.path.exists("audit_configs.json"):
        try:
            with open("audit_configs.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

def save_audit_config(name, config_data):
    configs = load_audit_configs()
    configs[name] = config_data
    with open("audit_configs.json", "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=2, ensure_ascii=False)

def get_denormalized_rules(base_url, api_key, doc_id):
    rules_records, err1 = fetch_table_records(base_url, api_key, doc_id, '_grist_ACLRules')
    resources_records, err2 = fetch_table_records(base_url, api_key, doc_id, '_grist_ACLResources')
    if err1 or err2:
        st.error(i18n[st.session_state.lang]["err_fetch_rules"].format(e=err1 or err2))
        return []
    if not rules_records: return []
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
        denormalized.append({
            "ID Regra": rule['id'],
            "Recurso": res_map.get(res_id, "Geral"),
            "Condição": fields.get('aclFormula') or "(Sempre)",
            "Permissões": fields.get('permissionsText'),
            "Memo": fields.get('memo') or "",
            "Posição": fields.get('rulePos')
        })
    denormalized.sort(key=lambda x: x.get('Posição', 0))
    return denormalized

def backup_rules_locally(doc_name, rules_data):
    try:
        if not os.path.exists("backups"): os.makedirs("backups")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fn = f"backups/rules_{doc_name.replace(' ', '_')}_{ts}.json"
        with open(fn, "w", encoding="utf-8") as f:
            json.dump(rules_data, f, indent=2, ensure_ascii=False)
        return True, fn
    except Exception as e: return False, str(e)

def apply_denormalized_rules(base_url, api_key, doc_id, new_rules_json):
    base_url = base_url.strip().rstrip("/")
    current, err1 = fetch_table_records(base_url, api_key, doc_id, '_grist_ACLRules')
    if current:
        ids_to_del = [r['id'] for r in current]
        url_del = f"{base_url}/docs/{doc_id}/tables/_grist_ACLRules/data/delete"
        requests.post(url_del, headers=get_auth_headers(api_key), json=ids_to_del)
    all_res, err2 = fetch_table_records(base_url, api_key, doc_id, '_grist_ACLResources')
    res_map = {}
    for r in all_res:
        rf = r['fields']
        res_map[f"{rf.get('tableId') or '*'}|{rf.get('colIds') or '*'}"] = r['id']
    records_to_add = []
    for i, rule in enumerate(new_rules_json):
        r_str = rule.get('Recurso', 'Geral')
        if "[" in r_str and r_str.endswith("]"):
            parts = r_str.split(" [")
            tid, cids = parts[0].strip(), parts[1].rstrip("]").strip()
        else: tid, cids = r_str.strip(), "*"
        key = f"{tid}|{cids}"
        res_id = res_map.get(key)
        if not res_id:
            url_res = f"{base_url}/docs/{doc_id}/tables/_grist_ACLResources/records"
            resp = requests.post(url_res, headers=get_auth_headers(api_key), json={'records': [{'fields': {'tableId': tid, 'colIds': cids}}]})
            if resp.status_code == 200:
                res_id = resp.json()['records'][0]['id']
                res_map[key] = res_id
            else: raise Exception(f"Falha recurso: {resp.text}")
        records_to_add.append({'fields': {'resource': res_id, 'aclFormula': rule.get('Condição', ''), 'permissionsText': rule.get('Permissões', ''), 'memo': rule.get('Memo', ''), 'rulePos': i + 1}})
    if records_to_add:
        url_add = f"{base_url}/docs/{doc_id}/tables/_grist_ACLRules/records"
        requests.post(url_add, headers=get_auth_headers(api_key), json={'records': records_to_add})
    return True

# 3. Main UI Layout
# --- Header Row (Title, Language, Global Help) ---
h_col1, h_col2, h_col3 = st.columns([3, 1, 0.2])

with h_col1:
    st.subheader(i18n[st.session_state.lang]['main_title'])

with h_col2:
    lang_options = {'en': '🇺🇸 English', 'pt': '🇧🇷 Português'}
    sel_lang = st.selectbox(
        "Language", 
        options=list(lang_options.keys()), 
        format_func=lambda x: lang_options[x], 
        index=0 if st.session_state.lang == 'en' else 1, 
        key="main_lang_selector",
        label_visibility="collapsed"
    )
    if sel_lang != st.session_state.lang:
        st.session_state.lang = sel_lang
        st.rerun()

with h_col3:
    help_url = "?nav=help"
    st.markdown(
        f'<a href="{help_url}" target="_blank" style="text-decoration: none; font-size: 1.5rem;" title="View Documentation">❓</a>',
        unsafe_allow_html=True
    )

st.divider()

# --- Deep Linking & Tab Help Icons ---
if 'nav' in st.query_params:
    st.session_state.main_nav_menu_key = st.query_params['nav']

def render_help_icon(anchor):
    """Renders a small help icon that links to the documentation section."""
    help_url = f"?nav=help#{anchor}"
    st.markdown(
        f"""
        <div style="text-align: right; margin-top: -50px; margin-bottom: 10px;">
            <a href="{help_url}" target="_blank" style="text-decoration: none; font-size: 1.5rem;" title="Help for this section">❓</a>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Sidebar: Connection ---
st.sidebar.markdown(i18n[st.session_state.lang]['sidebar_version'])
st.sidebar.header(i18n[st.session_state.lang]['sidebar_conn_header'])
saved_servers = load_saved_servers()
server_options = ["Grist Cloud (SaaS)"] + list(saved_servers.keys()) + [i18n[st.session_state.lang]['sidebar_add_server']]
if "auth_api_key" not in st.session_state: st.session_state.auth_api_key = os.getenv("GRIST_API_KEY", "")
if "auth_base_url" not in st.session_state: st.session_state.auth_base_url = "https://docs.getgrist.com/api"

selected_server = st.sidebar.selectbox(i18n[st.session_state.lang]['sidebar_server'], server_options, index=0 if st.session_state.auth_base_url == "https://docs.getgrist.com/api" else (server_options.index(st.session_state.auth_base_url) if st.session_state.auth_base_url in server_options else 0))
if selected_server == i18n[st.session_state.lang]['sidebar_add_server']:
    custom_url = st.sidebar.text_input(i18n[st.session_state.lang]['sidebar_new_url'])
elif selected_server == "Grist Cloud (SaaS)":
    st.session_state.auth_base_url = "https://docs.getgrist.com/api"
else:
    st.session_state.auth_base_url = selected_server
    if saved_servers.get(selected_server): st.session_state.auth_api_key = saved_servers[selected_server]

api_key_input = st.sidebar.text_input(i18n[st.session_state.lang]['sidebar_api_key'], value=st.session_state.auth_api_key, type="password")
save_creds = st.sidebar.checkbox(i18n[st.session_state.lang]['sidebar_save_key'], value=True)

if st.sidebar.button(i18n[st.session_state.lang]['sidebar_connect_btn']):
    if selected_server == i18n[st.session_state.lang]['sidebar_add_server'] and custom_url:
        st.session_state.auth_base_url = custom_url.strip().rstrip("/")
    st.session_state.auth_api_key = api_key_input
    if save_creds and st.session_state.auth_base_url != "https://docs.getgrist.com/api":
        save_server(st.session_state.auth_base_url, api_key_input)
    st.cache_data.clear(); st.session_state.mapped_data = None; st.success(i18n[st.session_state.lang]["msg_ok"]); st.rerun()

if not st.session_state.auth_api_key: st.warning(i18n[st.session_state.lang]["warn_key_needed"]); st.stop()
AUTH_API_KEY, AUTH_BASE_URL = st.session_state.auth_api_key, st.session_state.auth_base_url

# --- Sidebar: Org ---
st.sidebar.divider()
orgs = get_orgs(AUTH_BASE_URL, AUTH_API_KEY)
if not orgs: st.warning(i18n[st.session_state.lang]["warn_no_org"]); st.stop()
org_map = {f"{org['name']} ({org['id']})": org['id'] for org in orgs}
org_domain_map = {org['id']: org.get('domain') for org in orgs}
keys_list = list(org_map.keys())
default_idx = next((i for i, k in enumerate(keys_list) if "Qualidade Contábil" in k), 0)
selected_org_key = st.sidebar.selectbox(i18n[st.session_state.lang]['sidebar_org'], keys_list, index=default_idx)
selected_org_id, selected_org_name = org_map[selected_org_key], selected_org_key
selected_domain = org_domain_map.get(selected_org_id)

if "mapped_data" not in st.session_state: st.session_state.mapped_data = None
is_grist_cloud = "getgrist.com" in AUTH_BASE_URL
if selected_domain and "personal" not in selected_org_name.lower() and is_grist_cloud:
    CURRENT_BASE_URL = f"https://{selected_domain}.getgrist.com/api"
else: CURRENT_BASE_URL = AUTH_BASE_URL

st.sidebar.caption(f"📍 Base URL: {CURRENT_BASE_URL}")
if st.sidebar.button(i18n[st.session_state.lang]['sidebar_reload_btn']): st.cache_data.clear(); st.session_state.mapped_data = None; st.rerun()

# --- Sidebar: Menu ---
st.sidebar.divider()
st.sidebar.header(i18n[st.session_state.lang]['sidebar_main_menu_header'])
render_help_icon("sidebar")

# Navigation mapping to keep keys stable
menu_map = {
    'access': i18n[st.session_state.lang]['menu_access'],
    'data': i18n[st.session_state.lang]['menu_data'],
    'limits': i18n[st.session_state.lang]['tab_limits'],
    'help': i18n[st.session_state.lang]['tab_help']
}
main_menu_key = st.sidebar.selectbox(
    i18n[st.session_state.lang]['sidebar_go_to'], 
    options=list(menu_map.keys()), 
    format_func=lambda x: menu_map[x],
    key="main_nav_menu_key"
)

if main_menu_key == 'access':
    # Load mapping cache early so it's available when tab1 renders
    MAPPING_FILE = "mapping_cache.json"
    if st.session_state.mapped_data is None and os.path.exists(MAPPING_FILE):
        try:
            with open(MAPPING_FILE, "r", encoding="utf-8") as f:
                cache = json.load(f)
                if cache.get("org_id") == selected_org_id:
                    df_c = pd.DataFrame(cache["data"])
                    cols = ['Selecionar', 'Documento', 'Email', 'Nome', 'Nível de Acesso', 'Workspace', 'Doc ID']
                    for c in cols:
                        if c not in df_c.columns: df_c[c] = "-"
                    st.session_state.mapped_data = df_c
                    st.session_state.mapping_ts = cache.get("timestamp")
        except: pass

    tab1, tab2, tab3, tab4 = st.tabs([
        i18n[st.session_state.lang]['tab_global_view'],
        i18n[st.session_state.lang]['tab_mapping'],
        i18n[st.session_state.lang]['tab_quick_actions'],
        i18n[st.session_state.lang]['tab_acl']
    ])
    
    with tab1:
        st.header(i18n[st.session_state.lang]['header_users'].format(org=selected_org_name))
        render_help_icon("global-view")
        c1, c2 = st.columns(2)
        f_name = c1.text_input(i18n[st.session_state.lang]['filter_name'], key="s_g_name")
        f_email = c2.text_input(i18n[st.session_state.lang]['filter_email'], key="s_g_email")
        users = get_org_users(CURRENT_BASE_URL, AUTH_API_KEY, selected_org_id)
        if users:
            df_users = pd.DataFrame(users)
            df_display = df_users.rename(columns={'email': 'Email', 'name': 'Nome', 'access': 'Acesso Global'})
            
            # Map email-to-document count if mapping cache is loaded
            if st.session_state.mapped_data is not None:
                df_map = st.session_state.mapped_data
                df_valid_map = df_map[df_map['Email'] != '-']
                doc_counts = {}
                for idx, row in df_valid_map.iterrows():
                    em = str(row['Email']).strip().lower()
                    doc_counts[em] = doc_counts.get(em, set())
                    doc_counts[em].add(row['Doc ID'])
                
                doc_counts = {em: len(s) for em, s in doc_counts.items()}
                df_display['Documentos'] = df_display['Email'].apply(lambda x: doc_counts.get(str(x).strip().lower(), 0))
            else:
                df_display['Documentos'] = "Mapeamento Pendente"
                
            # Add Select column for batch actions
            df_display.insert(0, 'Selecionar', False)
            
            disp_cols = [c for c in ['Selecionar', 'Email', 'Nome', 'Acesso Global', 'Documentos'] if c in df_display.columns]
            df_display = df_display[disp_cols]
            
            if f_name: df_display = df_display[df_display['Nome'].str.contains(f_name, case=False, na=False)]
            if f_email: df_display = df_display[df_display['Email'].str.contains(f_email, case=False, na=False)]
            
            # Orphan filter checkbox
            if st.session_state.mapped_data is not None:
                show_orphans = st.checkbox("🔍 Mostrar apenas usuários órfãos (sem acesso a nenhum documento)", key="chk_show_orphans")
                if show_orphans:
                    df_display = df_display[df_display['Documentos'] == 0]
                    
            st.markdown(f"**Total de usuários exibidos:** `{len(df_display)}`")
            
            # Render as interactive data editor
            edited_users_df = st.data_editor(
                df_display, 
                use_container_width=True, 
                hide_index=True, 
                key="users_list_editor",
                disabled=[c for c in df_display.columns if c != 'Selecionar']
            )
            
            # Batch removal button
            selected_users = edited_users_df[edited_users_df['Selecionar'] == True]
            if not selected_users.empty:
                st.write("")
                if st.button("🔴 Remover Usuários Selecionados da Organização", type="secondary", key="btn_remove_org_users"):
                    with st.spinner("Removendo usuários..."):
                        for idx, row in selected_users.iterrows():
                            e = row['Email']
                            update_org_access(CURRENT_BASE_URL, AUTH_API_KEY, selected_org_id, e, None)
                        st.success(f"{len(selected_users)} usuários removidos da organização!")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
            
            with st.expander(i18n[st.session_state.lang]['header_org_invite']):
                c_inv1, c_inv2 = st.columns([3, 1])
                emails_inv = c_inv1.text_area(i18n[st.session_state.lang]['emails_to_invite'], key="emails_inv_org")
                
                # Role mapping for organization levels
                org_roles = {
                    i18n[st.session_state.lang]['role_owners']: "owners",
                    i18n[st.session_state.lang]['role_editors']: "editors",
                    i18n[st.session_state.lang]['role_viewers']: "viewers",
                    i18n[st.session_state.lang]['role_members']: "members"
                }
                role_inv_label = c_inv2.selectbox(i18n[st.session_state.lang]['level'], options=list(org_roles.keys()), key="role_inv_org")
                role_inv = org_roles[role_inv_label]
                
                if st.button(i18n[st.session_state.lang]['btn_invite'], key="btn_inv_org"):
                    list_inv = [e.strip().lower() for e in re.split(r'[,\s\n]+', emails_inv) if e.strip()]
                    for e in list_inv:
                        update_org_access(CURRENT_BASE_URL, AUTH_API_KEY, selected_org_id, e, role_inv)
                    st.success(i18n[st.session_state.lang]['toast_invited'])
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()

            st.divider()
            st.subheader(i18n[st.session_state.lang]['user_details'])
            if st.session_state.mapped_data is not None:
                valid_emails = sorted([e for e in df_display['Email'].unique() if e and e != '-'])
                sel_u = st.selectbox(i18n[st.session_state.lang]['select_user'], valid_emails, key="sel_u_det")
                if sel_u:
                    user_docs = st.session_state.mapped_data[st.session_state.mapped_data['Email'] == sel_u]
                    if 'Nível de Acesso' in user_docs.columns:
                        user_docs = user_docs[~user_docs['Nível de Acesso'].str.contains("Herdado", case=False, na=False)]
                    if not user_docs.empty:
                        d_cols = [c for c in ['Documento', 'Workspace', 'Nível de Acesso'] if c in user_docs.columns]
                        st.dataframe(user_docs[d_cols], use_container_width=True, hide_index=True)
                    else: st.warning(i18n[st.session_state.lang]['no_direct_access'])
            else: st.info(i18n[st.session_state.lang]['do_mapping_tab2'])

    with tab2:
        st.header(i18n[st.session_state.lang]['header_doc_mapping'])
        render_help_icon("mapping")
        MAPPING_FILE = "mapping_cache.json"
        if getattr(st.session_state, 'mapping_ts', None): st.caption(f"📅 {st.session_state.mapping_ts}")
        if st.button(i18n[st.session_state.lang]['btn_start_mapping'], key="start_map_btn"):
            with st.status(i18n[st.session_state.lang]['status_scanning']) as status:
                wss = get_workspaces_and_docs(CURRENT_BASE_URL, AUTH_API_KEY, selected_org_id)
                all_docs = [{'id': d['id'], 'name': d['name'], 'ws': ws.get('name')} for ws in wss for d in ws.get('docs', [])]
                consolidated = []
                for doc in all_docs:
                    doc_users = get_doc_users(CURRENT_BASE_URL, AUTH_API_KEY, doc['id'])
                    if doc_users:
                        for u in doc_users:
                            consolidated.append({'Selecionar': False, 'Documento': doc['name'], 'Email': u.get('email', ""), 'Nome': u.get('name', ""), 'Nível de Acesso': u.get('access') or f"{u.get('parentAccess')} (Herdado)", 'Workspace': doc['ws'], 'Doc ID': doc['id']})
                    else: consolidated.append({'Selecionar': False, 'Documento': doc['name'], 'Email': '-', 'Nome': '-', 'Nível de Acesso': 'Indefinido', 'Workspace': doc['ws'], 'Doc ID': doc['id']})
                df_map = pd.DataFrame(consolidated)
                cols = ['Selecionar', 'Documento', 'Email', 'Nome', 'Nível de Acesso', 'Workspace', 'Doc ID']
                for c in cols:
                    if c not in df_map.columns: df_map[c] = "-"
                st.session_state.mapped_data = df_map
                ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                st.session_state.mapping_ts = ts
                with open(MAPPING_FILE, "w", encoding="utf-8") as f: json.dump({"org_id": selected_org_id, "timestamp": ts, "data": consolidated}, f, indent=2, ensure_ascii=False)
                status.update(label="OK!", state="complete")
        if st.session_state.mapped_data is not None:
            df = st.session_state.mapped_data
            st.markdown(i18n[st.session_state.lang]['filters'])
            h_inh = st.checkbox(i18n[st.session_state.lang]['hide_inherited'], value=True)
            c1, c2, c3, c4 = st.columns(4)
            f_d, f_e, f_n, f_a = c1.text_input(i18n[st.session_state.lang]['doc']), c2.text_input(i18n[st.session_state.lang]['email']), c3.text_input(i18n[st.session_state.lang]['name']), c4.text_input(i18n[st.session_state.lang]['access'])
            df_f = df.copy()
            if h_inh: df_f = df_f[~df_f['Nível de Acesso'].str.contains("Herdado|Indefinido", case=False, na=False)]
            if f_d: df_f = df_f[df_f['Documento'].str.contains(f_d, case=False, na=False)]
            if f_e: df_f = df_f[df_f['Email'].str.contains(f_e, case=False, na=False)]
            if f_n: df_f = df_f[df_f['Nome'].str.contains(f_n, case=False, na=False)]
            if f_a: df_f = df_f[df_f['Nível de Acesso'].str.contains(f_a, case=False, na=False)]
            st.info(i18n[st.session_state.lang]['showing_x_of_y'].format(x=len(df_f), y=len(df)))
            if st.button(i18n[st.session_state.lang]['btn_sel_all']): st.session_state.mapped_data.loc[df_f.index, 'Selecionar'] = True; st.rerun()
            if st.button(i18n[st.session_state.lang]['btn_clear_sel']): st.session_state.mapped_data['Selecionar'] = False; st.rerun()
            def st_acc(v):
                v = str(v).lower()
                if 'owner' in v: return 'background-color: #ffcccc'
                if 'editor' in v: return 'background-color: #cce5ff'
                if 'viewer' in v: return 'background-color: #e6ffcc'
                return 'color: #999'
            styled = df_f.style.map(st_acc, subset=['Nível de Acesso']) if 'Nível de Acesso' in df_f.columns else df_f
            edited = st.data_editor(styled, use_container_width=True, hide_index=True, column_config={"Doc ID": None, "Selecionar": st.column_config.CheckboxColumn("Sel")}, disabled=["Documento", "Email", "Nome", "Nível de Acesso", "Workspace"], key="ed_map")
            sel = edited[edited['Selecionar']]
            if not sel.empty:
                st.divider(); st.subheader(i18n[st.session_state.lang]['operations'].format(count=len(sel)))
                all_docs = st.session_state.mapped_data[['Documento', 'Doc ID']].drop_duplicates()
                doc_opts = {r['Documento']: r['Doc ID'] for _, r in all_docs.iterrows()}
                c_a, c_b = st.columns(2)
                dest = c_a.selectbox(i18n[st.session_state.lang]['dest_doc'], sorted(doc_opts.keys()), index=None)
                if c_a.button(i18n[st.session_state.lang]['btn_copy'], disabled=not dest):
                    tid = doc_opts[dest]
                    for _, row in sel.iterrows():
                        rl = 'editors'
                        if 'owner' in str(row.get('Nível de Acesso','')).lower(): rl = 'owners'
                        elif 'viewer' in str(row.get('Nível de Acesso','')).lower(): rl = 'viewers'
                        if row.get('Email') != '-': update_doc_access(CURRENT_BASE_URL, AUTH_API_KEY, tid, row['Email'], rl)
                    st.toast(i18n[st.session_state.lang]['toast_copy_ok']); st.cache_data.clear(); time.sleep(1); st.rerun()
                new_l = c_b.selectbox(i18n[st.session_state.lang]['new_level'], ["viewers", "editors", "owners"])
                if c_b.button(i18n[st.session_state.lang]['btn_update']):
                    for _, row in sel.iterrows():
                        if row.get('Email') != '-': update_doc_access(CURRENT_BASE_URL, AUTH_API_KEY, row['Doc ID'], row['Email'], new_l)
                    st.toast(i18n[st.session_state.lang]['toast_updated']); st.cache_data.clear(); time.sleep(1); st.rerun()

    with tab3:
        st.header(i18n[st.session_state.lang]['header_quick_actions'])
        render_help_icon("quick-actions")
        if st.session_state.mapped_data is not None:
            all_q = st.session_state.mapped_data[['Documento', 'Doc ID']].drop_duplicates()
            doc_opts_q = {r['Documento']: r['Doc ID'] for _, r in all_q.iterrows()}
            target_q = st.selectbox(i18n[st.session_state.lang]['select_doc'], sorted(doc_opts_q.keys()), index=None)
            if target_q:
                tid = doc_opts_q[target_q]
                c1, c2 = st.columns(2)
                ems = c1.text_area(i18n[st.session_state.lang]['emails_add'])
                rl = c1.selectbox(i18n[st.session_state.lang]['level'], ["viewers", "editors", "owners"], key="q_rl")
                if c1.button(i18n[st.session_state.lang]['btn_add']):
                    list_e = [e.strip().lower() for e in re.split(r'[,\s\n]+', ems) if e.strip()]
                    # Safety Check: Compare with Org Users
                    org_users = get_org_users(CURRENT_BASE_URL, AUTH_API_KEY, selected_org_id)
                    org_emails = {u['email'].lower() for u in org_users if u.get('email')}
                    non_members = [e for e in list_e if e not in org_emails]
                    
                    if non_members:
                        st.session_state.pending_add = {"emails": list_e, "non_members": non_members, "tid": tid, "role": rl}
                    else:
                        for e in list_e: update_doc_access(CURRENT_BASE_URL, AUTH_API_KEY, tid, e, rl)
                        st.toast(i18n[st.session_state.lang]['toast_added']); st.cache_data.clear(); time.sleep(1); st.rerun()

                if "pending_add" in st.session_state:
                    p = st.session_state.pending_add
                    st.warning(i18n[st.session_state.lang]['warn_non_members'])
                    st.write(", ".join(p["non_members"]))
                    cw1, cw2, cw3 = st.columns([1.5, 1, 0.5])
                    if cw1.button(i18n[st.session_state.lang]['btn_add_to_org_first']):
                        for e in p["non_members"]:
                            update_org_access(CURRENT_BASE_URL, AUTH_API_KEY, selected_org_id, e, "viewers")
                        for e in p["emails"]:
                            update_doc_access(CURRENT_BASE_URL, AUTH_API_KEY, p["tid"], e, p["role"])
                        del st.session_state.pending_add
                        st.toast(i18n[st.session_state.lang]['toast_added']); st.cache_data.clear(); time.sleep(1); st.rerun()
                    if cw2.button(i18n[st.session_state.lang]['btn_proceed_guest']):
                        for e in p["emails"]:
                            update_doc_access(CURRENT_BASE_URL, AUTH_API_KEY, p["tid"], e, p["role"])
                        del st.session_state.pending_add
                        st.toast(i18n[st.session_state.lang]['toast_added']); st.cache_data.clear(); time.sleep(1); st.rerun()
                    if cw3.button("❌", help="Cancelar"):
                        del st.session_state.pending_add
                        st.rerun()

                ems_r = c2.text_area(i18n[st.session_state.lang]['emails_remove'])
                if c2.button(i18n[st.session_state.lang]['btn_remove'], type="primary"):
                    list_er = [e.strip().lower() for e in re.split(r'[,\s\n]+', ems_r) if e.strip()]
                    for e in list_er: update_doc_access(CURRENT_BASE_URL, AUTH_API_KEY, tid, e, None)
                    st.toast(i18n[st.session_state.lang]['toast_removed']); st.cache_data.clear(); time.sleep(1); st.rerun()
        else: st.info(i18n[st.session_state.lang]['mapping_needed'])

    with tab4:
        st.header(i18n[st.session_state.lang]['header_acl'])
        render_help_icon("acl")
        if st.session_state.mapped_data is not None:
            all_r = st.session_state.mapped_data[['Documento', 'Doc ID']].drop_duplicates()
            doc_opts_r = {r['Documento']: r['Doc ID'] for _, r in all_r.iterrows()}
        else:
            wss = get_workspaces_and_docs(CURRENT_BASE_URL, AUTH_API_KEY, selected_org_id)
            doc_opts_r = {d['name']: d['id'] for ws in wss for d in ws.get('docs', [])}
        target_r = st.selectbox(i18n[st.session_state.lang]["doc_audit"], sorted(doc_opts_r.keys()), index=None)
        if target_r:
            tid_r = doc_opts_r[target_r]
            st1, st2 = st.tabs([i18n[st.session_state.lang]["tab_view"], i18n[st.session_state.lang]["tab_edit"]])
            with st1:
                if st.button(i18n[st.session_state.lang]["btn_load"]):
                    rules = get_denormalized_rules(CURRENT_BASE_URL, AUTH_API_KEY, tid_r)
                    st.session_state.acl_data = rules
                if getattr(st.session_state, 'acl_data', None):
                    df_r = pd.DataFrame(st.session_state.acl_data)
                    st.dataframe(df_r, use_container_width=True, hide_index=True)
            with st2:
                if st.button(i18n[st.session_state.lang]["btn_gen_json"]):
                    rules = get_denormalized_rules(CURRENT_BASE_URL, AUTH_API_KEY, tid_r)
                    clean_rules = []
                    for r in rules:
                        cr = r.copy()
                        if "ID Regra" in cr: del cr["ID Regra"]
                        clean_rules.append(cr)
                    st.session_state.acl_editor_area = json.dumps(clean_rules, indent=2, ensure_ascii=False)

                ed_json = st.text_area(i18n[st.session_state.lang]["new_json_rules"], key="acl_editor_area", height=400)
                if st.button(i18n[st.session_state.lang]["btn_apply"]):
                    try:
                        new_r = json.loads(ed_json)
                        cur = get_denormalized_rules(CURRENT_BASE_URL, AUTH_API_KEY, tid_r)
                        ok_b, pb = backup_rules_locally(target_r, cur)
                        if ok_b:
                            apply_denormalized_rules(CURRENT_BASE_URL, AUTH_API_KEY, tid_r, new_r)
                            st.success(i18n[st.session_state.lang]["toast_applied"]); st.cache_data.clear()
                    except Exception as e: st.error(i18n[st.session_state.lang]["err_generic"].format(e=e))

elif main_menu_key == 'data':
    tab7, tab_trans, tab_import, tab6, tab8, tab10 = st.tabs([
        i18n[st.session_state.lang]['tab_cloner'],
        i18n[st.session_state.lang]['tab_transporter'],
        i18n[st.session_state.lang].get('tab_import', '📥 Importador CSV/JSON'),
        i18n[st.session_state.lang]['tab_audit'],
        i18n[st.session_state.lang]['tab_blueprint'],
        i18n[st.session_state.lang]['tab_ai']
    ])
    
    with tab7:
        st.header(i18n[st.session_state.lang]['tab_cloner'])
        render_help_icon("cloner")
        if st.session_state.mapped_data is not None:
            all_c = st.session_state.mapped_data[['Documento', 'Doc ID']].drop_duplicates()
            doc_opts_c = {r['Documento']: r['Doc ID'] for _, r in all_c.iterrows()}
        else:
            wss = get_workspaces_and_docs(CURRENT_BASE_URL, AUTH_API_KEY, selected_org_id)
            doc_opts_c = {d['name']: d['id'] for ws in wss for d in ws.get('docs', [])}
        c1, c2 = st.columns(2)
        src_n = c1.selectbox(i18n[st.session_state.lang]['doc_source'], sorted(doc_opts_c.keys()), index=None, key="c_src")
        if src_n:
            sid = doc_opts_c[src_n]
            tables = get_tables(CURRENT_BASE_URL, AUTH_API_KEY, sid)
            tbl_id = c2.selectbox(i18n[st.session_state.lang]['lbl_table'], sorted([t['id'] for t in tables]), index=None)
            if tbl_id:
                cols = get_columns(CURRENT_BASE_URL, AUTH_API_KEY, sid, tbl_id)
                clean = []
                for c in cols:
                    f = c['fields']
                    clean.append({"id": c['id'], "fields": {"label": f.get("label"), "type": f.get("type"), "isFormula": f.get("isFormula", False), "formula": f.get("formula", ""), "widgetOptions": f.get("widgetOptions", "")}})
                targets = st.multiselect(i18n[st.session_state.lang]['lbl_targets'], sorted(doc_opts_c.keys()))
                if st.button(i18n[st.session_state.lang]["btn_clone"]):
                    for tn in targets:
                        tid = doc_opts_c[tn]
                        ok, msg = create_table(CURRENT_BASE_URL, AUTH_API_KEY, tid, tbl_id, clean)
                        if msg == "EXISTING": add_columns(CURRENT_BASE_URL, AUTH_API_KEY, tid, tbl_id, clean)
                    st.success(i18n[st.session_state.lang]["toast_completed"])

    with tab_trans:
        st.header(i18n[st.session_state.lang]["header_transporter"])
        render_help_icon("transporter")
        if st.session_state.mapped_data is not None:
            m_data = st.session_state.mapped_data
            all_t = m_data[['Documento', 'Doc ID']].drop_duplicates()
            doc_opts_t = {r['Documento']: r['Doc ID'] for _, r in all_t.iterrows()}
            c1, c2 = st.columns(2)
            src_n = c1.selectbox(i18n[st.session_state.lang]['doc_source'], sorted(doc_opts_t.keys()), index=None, key="t_src")
            if src_n:
                sid = doc_opts_t[src_n]
                tables = get_tables(CURRENT_BASE_URL, AUTH_API_KEY, sid)
                sel_tbls = c2.multiselect(i18n[st.session_state.lang]['lbl_tables_to_transport'], sorted([t['id'] for t in tables if not t['id'].startswith('_grist')]))
                dest_n = st.selectbox(i18n[st.session_state.lang]["t_dest_doc"], sorted(doc_opts_t.keys()), index=None, key="t_dest")
                
                if sel_tbls and dest_n:
                    did = doc_opts_t[dest_n]
                    
                    # Reset state if source/dest or selection changes
                    current_sig = f"{sid}-{did}-{'-'.join(sel_tbls)}"
                    if st.session_state.get("t_sig") != current_sig:
                        st.session_state.t_sig = current_sig
                        st.session_state.t_step = 0
                        st.session_state.t_logs = ["ℹ️ Aguardando início..."]
                        st.session_state.t_tasks = []
                        st.session_state.t_src_map = {}
                        
                    st.progress(st.session_state.t_step / 3.0)
                    
                    c_btn1, c_btn2, c_btn3, c_btn4 = st.columns(4)
                    
                    if st.session_state.t_step == 0:
                        if c_btn1.button(i18n[st.session_state.lang]['btn_phase1'], type="primary"):
                            st.session_state.t_logs = ["--- INICIANDO FASE 1 (ESTRUTURA INTELIGENTE) ---"]
                            
                            # Topological sort to handle references (Parents first)
                            graph = {t: [] for t in sel_tbls}
                            schemas = {}
                            for t in sel_tbls:
                                cols = get_columns(CURRENT_BASE_URL, AUTH_API_KEY, sid, t)
                                schemas[t] = cols
                                for c in cols:
                                    t_val = str(c['fields'].get('type', ''))
                                    if t_val.startswith('Ref:'):
                                        ref_t = t_val.split(':')[1]
                                        if ref_t in sel_tbls and ref_t != t:
                                            graph[t].append(ref_t)
                            
                            visited, temp, order = set(), set(), []
                            def visit(n):
                                if n in temp or n in visited: return
                                temp.add(n)
                                for m in graph.get(n, []): visit(m)
                                temp.remove(n)
                                visited.add(n)
                                order.append(n)
                            for t in sel_tbls: visit(t)
                            
                            st.session_state.t_logs.append(f"🧩 Ordem de processamento (Dependências resolvidas): {', '.join(order)}")
                            
                            table_tasks = []
                            source_col_map = {}
                            
                            for tid in order:
                                st.session_state.t_logs.append(f"\n➤ Processando Tabela: {tid}")
                                cols = schemas[tid]
                                p1_schema = []
                                full_schema = []
                                fids = set()
                                
                                for c in cols:
                                    cid_str = c['id']
                                    if cid_str == 'manualSort': continue
                                    f = c['fields']
                                    
                                    # Cache source mapping
                                    source_col_map[(tid, cid_str)] = cid_str
                                    source_col_map[(tid, f.get('colRef'))] = cid_str
                                    
                                    full_schema.append({"id": cid_str, "fields": f})
                                    
                                    c_type = str(f.get('type', ''))
                                    
                                    # PHASE 1: Use 'Any' for References to avoid Sandbox/Circular errors
                                    # This is the "Atomic Strategy": Data first, Relations later.
                                    p1_type = c_type
                                    is_ref = c_type.startswith('Ref:')
                                    if is_ref:
                                        p1_type = 'Any'
                                    
                                    p1_fields = {
                                        "label": f.get('label'),
                                        "type": p1_type,
                                        "isFormula": False,
                                        "formula": ""
                                    }
                                    
                                    # For Choice/Ref, keep widgetOptions to setup native UI instantly
                                    if c_type == 'Choice' or is_ref:
                                        wopt_str = f.get('widgetOptions', '')
                                        # If it's a Ref, we strip widgetOptions in Phase 1 to be 100% safe
                                        # They will be restored in Phase 3.
                                        if is_ref:
                                            wopt_str = ''
                                        elif wopt_str:
                                            try:
                                                wopt = json.loads(wopt_str)
                                                if "dropdownCondition" in wopt:
                                                    del wopt["dropdownCondition"]
                                                    wopt_str = json.dumps(wopt)
                                                    st.session_state.t_logs.append(f"   ⚠️ Coluna '{cid_str}': dropdownCondition removido temporariamente.")
                                            except:
                                                pass
                                        
                                        p1_fields["widgetOptions"] = wopt_str
                                        if is_ref:
                                            ref_target = c_type.split(":")[1]
                                            st.session_state.t_logs.append(f"   🔗 Coluna '{cid_str}' (Ref -> {ref_target}) configurada como 'Any' para garantir inserção na Fase 2.")
                                    else:
                                        p1_fields["widgetOptions"] = ''
                                        st.session_state.t_logs.append(f"   - Coluna '{cid_str}' configurada como {c_type}")
                                        
                                    p1_schema.append({"id": cid_str, "fields": p1_fields})
                                    
                                    if f.get('isFormula') or cid_str.startswith('gristHelper'):
                                        fids.add(cid_str)
                                        
                                # PHASE 1: Second pass to inject our custom display helpers
                                # We do this after building p1_schema and full_schema
                                for c in cols:
                                    f = c['fields']
                                    c_type = str(f.get('type', ''))
                                    cid_str = c['id']
                                    
                                    if c_type.startswith('Ref:'):
                                        rt = c_type.split(':')[1]
                                        vid = f.get('visibleCol')
                                        if vid:
                                            vstr = source_col_map.get((rt, vid))
                                            if vstr:
                                                helper_id = f"z_disp_{cid_str}"
                                                
                                                # Add to Phase 1 creation payload as a plain 'Any' column
                                                p1_schema.append({
                                                    "id": helper_id,
                                                    "fields": {"label": helper_id, "type": "Any", "isFormula": False, "formula": ""}
                                                })
                                                
                                                # Add to full_schema so Phase 3 processes it as a formula
                                                full_schema.append({
                                                    "id": helper_id,
                                                    "fields": {
                                                        "type": "Any",
                                                        "isFormula": True,
                                                        "formula": f"${cid_str}.{vstr}",
                                                        "_is_custom_helper": True,
                                                        "for_ref_col": cid_str
                                                    }
                                                })
                                                fids.add(helper_id)
                                                st.session_state.t_logs.append(f"   🪄 Criando helper visual customizado '{helper_id}' para '{cid_str}'")

                                ok_c, m_c = create_table(CURRENT_BASE_URL, AUTH_API_KEY, did, tid, p1_schema)
                                if ok_c: st.session_state.t_logs.append(f"   ✅ Tabela {tid} criada com sucesso ({len(p1_schema)} colunas).")
                                else: st.session_state.t_logs.append(f"   ℹ️ Tabela {tid}: {m_c}")
                                
                                table_tasks.append({"id": tid, "fids": fids, "ready": ok_c or m_c == "EXISTING", "schema": full_schema})
                                
                            st.session_state.t_tasks = table_tasks
                            st.session_state.t_src_map = source_col_map
                            st.session_state.t_step = 1
                            st.session_state.t_logs.append("\n⏸️ FASE 1 CONCLUÍDA. Verifique o log e clique em 'Fase 2' para inserir os dados.")
                            st.rerun()

                    elif st.session_state.t_step == 1:
                        if c_btn2.button(i18n[st.session_state.lang]['btn_phase2'], type="primary"):
                            st.session_state.t_logs.append("\n--- INICIANDO FASE 2 (INSERÇÃO DE DADOS) ---")
                            for task in st.session_state.t_tasks:
                                tid = task["id"]
                                if not task["ready"]: continue
                                st.session_state.t_logs.append(f"➤ Lendo dados de: {tid}")
                                recs, err = fetch_table_records(CURRENT_BASE_URL, AUTH_API_KEY, sid, tid)
                                if err:
                                    st.session_state.t_logs.append(f"   ❌ Erro ao ler: {err}")
                                    continue
                                
                                date_cols = {c['id'] for c in task["schema"] if str(c['fields'].get('type')).startswith('Date')}
                                clean_r = []
                                for r in recs:
                                    row = {}
                                    for k, v in r['fields'].items():
                                        if k in task["fids"] or k.startswith('gristHelper') or k == 'manualSort': continue
                                        if k in date_cols and isinstance(v, (int, float)):
                                            try: v = datetime.fromtimestamp(v).strftime('%Y-%m-%d')
                                            except: pass
                                        row[k] = v
                                    clean_r.append(row)
                                
                                scnt = 0
                                for i in range(0, len(clean_r), 500):
                                    b = clean_r[i:i+500]
                                    ok, m = add_records(CURRENT_BASE_URL, AUTH_API_KEY, did, tid, b)
                                    if ok: scnt += len(b)
                                    else: st.session_state.t_logs.append(f"   ⚠️ Lote com erro: {m}")
                                st.session_state.t_logs.append(f"   ✅ {scnt} registros inseridos em {tid}.")
                            
                            st.session_state.t_step = 2
                            st.session_state.t_logs.append("\n⏸️ FASE 2 CONCLUÍDA. As referências já devem estar vinculadas. Clique em 'Fase 3' para reativar as Fórmulas.")
                            st.rerun()

                    elif st.session_state.t_step == 2:
                        if c_btn3.button(i18n[st.session_state.lang]['btn_phase3'], type="primary"):
                            st.session_state.t_logs.append("\n--- INICIANDO FASE 3 (ATIVAÇÃO DE FÓRMULAS E MAPPING) ---")
                            dest_col_map = {}
                            
                            def get_dest_id(t, c):
                                if t not in dest_col_map:
                                    dest_col_map[t] = {}
                                    try:
                                        d_cols = get_columns_no_cache(CURRENT_BASE_URL, AUTH_API_KEY, did, t)
                                        for dc in d_cols: dest_col_map[t][dc['id']] = dc['fields'].get('colRef')
                                    except: pass
                                return dest_col_map.get(t, {}).get(c)

                            for task in st.session_state.t_tasks:
                                if not task["ready"]: continue
                                tid = task["id"]
                                upd = []
                                st.session_state.t_logs.append(f"➤ Atualizando Metadados: {tid}")
                                
                                for col in task["schema"]:
                                    f = col['fields']
                                    cid = col['id']
                                    nf = {
                                        "type": f.get('type'),
                                        "isFormula": f.get('isFormula', False),
                                        "formula": f.get('formula', ''),
                                        "widgetOptions": f.get('widgetOptions', ''),
                                        "visibleCol": None, "displayCol": None
                                    }
                                    
                                    # If it's our injected helper, just push the formula update
                                    if f.get('_is_custom_helper'):
                                        nf['displayCol'] = 0
                                        nf['visibleCol'] = 0
                                        upd.append({"id": cid, "fields": nf})
                                        st.session_state.t_logs.append(f"   - {cid}: Fórmula ativada ('{nf['formula'][:30]}...')")
                                        continue
                                    
                                    # Resolve Reference mapping
                                    if str(f.get('type')).startswith("Ref:"):
                                        rt = str(f.get('type')).split(":")[1]
                                        vid = f.get('visibleCol')
                                        
                                        # Map visibleCol
                                        if vid and (rt, vid) in st.session_state.t_src_map:
                                            vstr = st.session_state.t_src_map[(rt, vid)]
                                            nvid = get_dest_id(rt, vstr)
                                            if nvid: nf["visibleCol"] = nvid
                                            st.session_state.t_logs.append(f"   - {cid}: visibleCol mapeado para '{vstr}' (ID {nvid})")
                                            
                                            # We generated a helper for this visibleCol in Phase 1! Let's find its ID in the dest table
                                            helper_name = f"z_disp_{cid}"
                                            ndid = get_dest_id(tid, helper_name)
                                            if ndid:
                                                nf["displayCol"] = ndid
                                                st.session_state.t_logs.append(f"   - {cid}: displayCol apontado para helper customizado '{helper_name}' (ID {ndid})")
                                            else:
                                                st.session_state.t_logs.append(f"   ⚠️ {cid}: displayCol não encontrou o helper customizado '{helper_name}'")
                                                nf["displayCol"] = 0
                                        else:
                                            nf["displayCol"] = 0
                                    
                                    if f.get('isFormula'):
                                        st.session_state.t_logs.append(f"   - {cid}: Fórmula ativada ('{nf['formula'][:30]}...')")
                                            
                                    upd.append({"id": cid, "fields": nf})
                                    
                                ok, m = update_columns(CURRENT_BASE_URL, AUTH_API_KEY, did, tid, upd)
                                if ok: st.session_state.t_logs.append(f"   ✅ Inteligência restaurada.")
                                else: st.session_state.t_logs.append(f"   ❌ Erro PATCH: {m}")
                            
                            st.session_state.t_step = 3
                            st.session_state.t_logs.append("\n🎉 TRANSPORTE TOTALMENTE CONCLUÍDO!")
                            st.balloons()
                            st.rerun()

                    if st.session_state.t_step > 0:
                        if c_btn4.button("🔄 Resetar / Abortar"):
                            st.session_state.t_step = 0
                            st.session_state.t_logs = ["ℹ️ Aguardando início..."]
                            st.rerun()

                    with st.container(border=True):
                        st.markdown(i18n[st.session_state.lang]["console_operations"])
                        st.code("\n".join(st.session_state.get("t_logs", [])), language="markdown")


            # --- NEW: TABLE INSPECTOR (FOR DEBUGGING) ---
            st.divider()
            with st.expander(i18n[st.session_state.lang]["inspector_debug"], expanded=False):
                st.markdown(i18n[st.session_state.lang]["inspector_desc"])
                
                # Check for mapped data inside the expander context or just use it
                all_docs_i = st.session_state.mapped_data[['Documento', 'Doc ID']].drop_duplicates()
                doc_opts_i = {r['Documento']: r['Doc ID'] for _, r in all_docs_i.iterrows()}
                
                col_i1, col_i2 = st.columns(2)
                insp_doc_name = col_i1.selectbox(i18n[st.session_state.lang]['doc_to_inspect'], sorted(doc_opts_i.keys()), index=None, key="insp_doc")
                
                if insp_doc_name:
                    insp_doc_id = doc_opts_i[insp_doc_name]
                    insp_tables = get_tables(CURRENT_BASE_URL, AUTH_API_KEY, insp_doc_id)
                    insp_table_id = col_i2.selectbox(i18n[st.session_state.lang]['lbl_table'], sorted([t['id'] for t in insp_tables]), index=None, key="insp_table")
                    
                    if insp_table_id:
                        col_btn1, col_i_rest = st.columns([1, 3])
                        if col_btn1.button(i18n[st.session_state.lang]['btn_inspect_all'], key="btn_load_raw"):
                            with st.spinner("Lendo Schema e Sandbox..."):
                                # 1. Fetch Metadata (Schema) including hidden columns
                                try:
                                    url_hidden = f"{CURRENT_BASE_URL}/docs/{insp_doc_id}/tables/{insp_table_id}/columns?hidden=true"
                                    response_hidden = requests.get(url_hidden, headers=get_auth_headers(AUTH_API_KEY))
                                    raw_cols = response_hidden.json().get('columns', [])
                                except Exception as e:
                                    st.error(i18n[st.session_state.lang]["err_read_hidden_schema"].format(e=e))
                                    raw_cols = []
                                st.session_state.insp_schema = raw_cols
                                
                                # 2. Fetch Records
                                raw_recs, err_i = fetch_table_records(CURRENT_BASE_URL, AUTH_API_KEY, insp_doc_id, insp_table_id)
                                if err_i:
                                    st.error(i18n[st.session_state.lang]["err_records"].format(err_i=err_i))
                                    st.session_state.insp_raw_df = None
                                else:
                                    data_for_df = []
                                    for r in raw_recs:
                                        row = {"_id": r['id']}
                                        row.update(r['fields'])
                                        data_for_df.append(row)
                                    st.session_state.insp_raw_df = pd.DataFrame(data_for_df)

                        # --- DISPLAY SECTION ---
                        if getattr(st.session_state, 'insp_schema', None) is not None:
                            st.subheader(i18n[st.session_state.lang]["col_metadata"])
                            schema_view = []
                            for c in st.session_state.insp_schema:
                                f = c['fields']
                                cid = c['id']
                                is_hidden = cid.startswith('gristHelper')
                                display_id = f"👻 {cid}" if is_hidden else cid
                                schema_view.append({
                                    "ID": display_id,
                                    "Label": f.get('label'),
                                    "Tipo": f.get('type'),
                                    "Fórmula?": f.get('isFormula'),
                                    "Fórmula": f.get('formula', ''),
                                    "Opções (widgetOptions)": f.get('widgetOptions', '')
                                })
                            
                            df_schema = pd.DataFrame(schema_view)
                            
                            def color_hidden(val):
                                if isinstance(val, str) and val.startswith("👻"):
                                    return 'color: gray; font-style: italic; background-color: #f0f2f6;'
                                return ''
                                
                            styled_schema = df_schema.style.map(color_hidden, subset=['ID'])
                            st.dataframe(styled_schema, use_container_width=True, hide_index=True)
                            
                            # Export Schema as JSON
                            st.markdown(i18n[st.session_state.lang]["json_schema"])
                            st.code(json.dumps(st.session_state.insp_schema, indent=2, ensure_ascii=False), language="json")

                        if getattr(st.session_state, 'insp_raw_df', None) is not None:
                            st.subheader(i18n[st.session_state.lang]["raw_records"])
                            df_insp = st.session_state.insp_raw_df.copy()
                            df_insp.insert(0, "Selecionar", False)
                            
                            edited_insp = st.data_editor(
                                df_insp,
                                use_container_width=True,
                                hide_index=True,
                                column_config={"Selecionar": st.column_config.CheckboxColumn("Sel", default=False)},
                                key="editor_insp_raw"
                            )
                            
                            sel_insp = edited_insp[edited_insp["Selecionar"]]
                            if not sel_insp.empty:
                                st.info(i18n[st.session_state.lang]["x_rows_selected"].format(count=len(sel_insp)))
                                export_json = sel_insp.drop(columns=["Selecionar"]).to_dict(orient='records')
                                json_str = json.dumps(export_json, indent=2, ensure_ascii=False)
                                st.markdown(i18n[st.session_state.lang]["json_data"])
                                st.code(json_str, language="json")
        else:
            st.info("Mapeamento necessário.")

    with tab_import:
        st.header(i18n[st.session_state.lang].get('tab_import', '📥 Importador CSV/JSON'))
        st.markdown(i18n[st.session_state.lang].get('import_desc', 'Importe arquivos CSV/JSON criando novas tabelas ou adicionando a tabelas existentes, com suporte a mapeamento inteligente de referências.'))
        
        # 1. Target Document Selection (directly from API, no mapped_data dependency!)
        wss = get_workspaces_and_docs(CURRENT_BASE_URL, AUTH_API_KEY, selected_org_id)
        doc_options = {d['name']: d['id'] for ws in wss for d in ws.get('docs', [])}
            
        target_doc_name = st.selectbox(
            i18n[st.session_state.lang].get('import_target_doc', 'Documento de Destino'),
            sorted(doc_options.keys()),
            index=None,
            key="import_target_doc_select"
        )
        
        if target_doc_name:
            target_doc_id = doc_options[target_doc_name]
            
            import_mode_selection = st.radio(
                "Escolha o Modo de Importação:",
                ["Individual (CSV Único)", "Relacional Completo (Schema JSON + Pasta CSV)"],
                horizontal=True,
                key="import_mode_selection_radio"
            )
            
            if import_mode_selection == "Relacional Completo (Schema JSON + Pasta CSV)":
                st.subheader("📥 Importação Relacional em Lote")
                st.markdown("Importe um banco de dados completo no Grist usando um arquivo Schema JSON (com metadados de FKs) e uma pasta contendo os CSVs dos dados.")
                
                c1, c2 = st.columns(2)
                schema_input = c1.text_input("Caminho do arquivo Schema JSON:", value=r"C:\customwidgets\sistemacalibracao\schema_and_data.json")
                csv_dir_input = c2.text_input("Caminho da pasta de CSVs:", value=r"C:\customwidgets\sistemacalibracao\csv")
                
                if st.button("Verificar Fontes e Mapeamento", key="btn_verify_relational"):
                    if not os.path.exists(schema_input):
                        st.error(f"Schema JSON não encontrado em: {schema_input}")
                    elif not os.path.exists(csv_dir_input):
                        st.error(f"Pasta de CSVs não encontrada em: {csv_dir_input}")
                    else:
                        try:
                            with open(schema_input, 'r', encoding='utf-8-sig') as f:
                                schema_data = json.load(f)
                            
                            tables = list(schema_data.get("Counts", {}).keys())
                            fks = schema_data.get("FKs", [])
                            
                            st.success("Schema JSON carregado com sucesso!")
                            st.write(f"**Tabelas detectadas:** {len(tables)} | **Relacionamentos (FK):** {len(fks)}")
                            
                            # Checklist
                            checklist = []
                            for t in sorted(tables):
                                csv_file = os.path.join(csv_dir_input, f"{t.lower()}.csv")
                                exists = os.path.exists(csv_file)
                                size_str = "N/A"
                                rows = "N/A"
                                if exists:
                                    size_bytes = os.path.getsize(csv_file)
                                    size_str = f"{size_bytes/1024:.2f} KB" if size_bytes < 1024*1024 else f"{size_bytes/(1024*1024):.2f} MB"
                                    try:
                                        if os.path.getsize(csv_file) <= 3:
                                            rows = 0
                                        else:
                                            rows = len(pd.read_csv(csv_file))
                                    except Exception:
                                        rows = 0
                                checklist.append({
                                    "Tabela": t,
                                    "CSV Encontrado": "✅ Sim" if exists else "❌ Não",
                                    "Registros": rows,
                                    "Tamanho": size_str
                                })
                            st.table(checklist)
                            
                            st.session_state.verified_relational_data = {
                                "schema_path": schema_input,
                                "csv_dir": csv_dir_input,
                                "tables": tables,
                                "fks": fks,
                                "columns": schema_data.get("Columns", []),
                                "previews": schema_data.get("Previews", {})
                            }
                        except Exception as e:
                            st.error(f"Erro ao carregar o Schema: {e}")
                
                if st.session_state.get("verified_relational_data"):
                    verify_info = st.session_state.verified_relational_data
                    
                    # 1. Reference detection configuration
                    st.write("---")
                    st.subheader("⚙️ Configuração da Detecção Automática de Chaves Estrangeiras (FK)")
                    ref_tags_input = st.text_input("Tags de identificação de ID (separadas por vírgula):", value="ID_, _ID, ID, FK, REF", key="ref_tags_input")
                    
                    search_tags = [t.strip().upper() for t in ref_tags_input.split(",") if t.strip()]
                    
                    # Compute detected candidates grouped by table
                    detected_fks = {}
                    for t in verify_info["tables"]:
                        # check if csv exists for this table
                        csv_file = os.path.join(verify_info["csv_dir"], f"{t.lower()}.csv")
                        if not os.path.exists(csv_file):
                            continue
                        
                        cols = [c for c in verify_info["columns"] if c['Table'] == t]
                        for c in cols:
                            col_id = c['Column']
                            if col_id.upper() == 'ID':
                                continue
                                
                            # Check tags
                            is_candidate = False
                            base_name = col_id
                            for tag in search_tags:
                                if tag.endswith('_') and col_id.upper().startswith(tag):
                                    is_candidate = True
                                    base_name = col_id[len(tag):]
                                    break
                                elif tag.startswith('_') and col_id.upper().endswith(tag):
                                    is_candidate = True
                                    base_name = col_id[:-len(tag)]
                                    break
                                elif col_id.upper().startswith(tag):
                                    is_candidate = True
                                    base_name = col_id[len(tag):]
                                    break
                                elif col_id.upper().endswith(tag):
                                    is_candidate = True
                                    base_name = col_id[:-len(tag)]
                                    break
                                    
                            # Check if matches any existing JSON FK
                            existing_fk = next((fk for fk in verify_info["fks"] if fk['Table'] == t and fk['Column'] == col_id), None)
                            
                            if is_candidate or existing_fk:
                                if t not in detected_fks:
                                    detected_fks[t] = []
                                    
                                # Guess target table
                                target_guess = existing_fk['ForeignTable'] if existing_fk else None
                                if not target_guess:
                                    clean_base = base_name.replace('_', '').lower().rstrip('s')
                                    for tbl in verify_info["tables"]:
                                        clean_t = tbl.replace('_', '').lower().rstrip('s')
                                        if clean_base == clean_t or clean_base in clean_t or clean_t in clean_base:
                                            target_guess = tbl
                                            break
                                            
                                detected_fks[t].append({
                                    "Column": col_id,
                                    "TargetGuess": target_guess,
                                    "Type": c['Type']
                                })
                                
                    # Display expanders for reviewing
                    st.write("---")
                    st.subheader("📋 Revisão de Relacionamentos por Tabela")
                    st.markdown("Revise os relacionamentos detectados. Você pode alterar a tabela destino ou o nome da coluna de exibição (ex: `NAME`, `CODE`, `ABBREVIATION`).")
                    
                    reviewed_fks = []
                    
                    for t, candidates in sorted(detected_fks.items()):
                        with st.expander(f"Tabela: {t} ({len(candidates)} relacionamentos detectados)", expanded=False):
                            for cand in candidates:
                                col_id = cand["Column"]
                                c1, c2, c3 = st.columns(3)
                                with c1:
                                    st.markdown(f"**Coluna:** `{col_id}`")
                                with c2:
                                    # Target table selection
                                    all_options = ["Nenhum"] + sorted(verify_info["tables"])
                                    def_idx = 0
                                    if cand["TargetGuess"] in all_options:
                                        def_idx = all_options.index(cand["TargetGuess"])
                                    target_selection = st.selectbox(
                                        "Tabela Destino",
                                        options=all_options,
                                        index=def_idx,
                                        key=f"fk_target_{t}_{col_id}"
                                    )
                                with c3:
                                    # Fetch target table columns
                                    target_cols = ["0"]
                                    if target_selection != "Nenhum":
                                        target_cols += sorted(list(set([col['Column'] for col in verify_info["columns"] if col['Table'] == target_selection])))
                                    
                                    # Suggest default display column (e.g. NAME or ABBREVIATION)
                                    def_col_idx = 0
                                    default_disp = "0"
                                    if target_selection == "MEASUREMENT_UNITS" and "ABBREVIATION" in target_cols:
                                        default_disp = "ABBREVIATION"
                                    elif target_selection in ["SITUATIONS", "SUPPLIERS", "USERS", "INSTRUMENTS_TYPES"] and "NAME" in target_cols:
                                        default_disp = "NAME"
                                    else:
                                        for sugg in ["NAME", "ABBREVIATION", "CODE", "DESCRIPTION"]:
                                            if sugg in target_cols:
                                                default_disp = sugg
                                                break
                                    
                                    if default_disp in target_cols:
                                        def_col_idx = target_cols.index(default_disp)
                                        
                                    display_col = st.selectbox(
                                        "Coluna de Exibição (visibleCol)",
                                        options=target_cols,
                                        index=def_col_idx,
                                        key=f"fk_disp_{t}_{col_id}"
                                    )
                                    
                                if target_selection != "Nenhum":
                                    reviewed_fks.append({
                                        "Table": t,
                                        "Column": col_id,
                                        "ForeignTable": target_selection,
                                        "DisplayCol": display_col if display_col != "0" else 0
                                    })
                                    
                                    # Target CSV status, preview, and on-demand extraction
                                    csv_file_target = os.path.join(verify_info["csv_dir"], f"{target_selection.lower()}.csv")
                                    csv_exists = os.path.exists(csv_file_target)
                                    
                                    stat_c, prev_c, act_c = st.columns([1, 1, 1])
                                    with stat_c:
                                        if csv_exists:
                                            st.markdown("✅ **CSV pronto**")
                                        else:
                                            st.markdown("❌ **CSV ausente**")
                                    with prev_c:
                                        previews = verify_info.get("previews", {})
                                        preview_rows = previews.get(target_selection, [])
                                        if preview_rows:
                                            with st.expander("👁️ Ver prévia (5 lin.)"):
                                                st.dataframe(pd.DataFrame(preview_rows).head(5), use_container_width=True, hide_index=True)
                                        else:
                                            st.caption("*Sem prévia disponível*")
                                    with act_c:
                                        if not csv_exists:
                                            if st.button(f"📥 Extrair {target_selection}", key=f"btn_extract_{t}_{col_id}"):
                                                with st.spinner(f"Extraindo {target_selection}..."):
                                                    try:
                                                        import subprocess
                                                        ps_cmd = [
                                                            r"C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe",
                                                            "-ExecutionPolicy", "Bypass",
                                                            "-File", r"C:\customwidgets\sistemacalibracao\export_tables_to_csv.ps1",
                                                            "-tables", target_selection
                                                        ]
                                                        res = subprocess.run(ps_cmd, capture_output=True, text=True)
                                                        if res.returncode == 0:
                                                            st.success("Exportado!")
                                                            st.rerun()
                                                        else:
                                                            st.error(f"Erro: {res.stderr}")
                                                    except Exception as ex:
                                                        st.error(str(ex))
                                    
                    st.session_state.reviewed_fks = reviewed_fks
                    
                    st.warning("⚠️ Atenção: A importação criará tabelas no documento. Se as tabelas já existirem, os dados serão adicionados.")
                    
                    if st.button("Iniciar Importação Relacional", type="primary", key="btn_run_relational"):
                        rel_log_area = st.empty()
                        rel_logs = ["🚀 Iniciando importação relacional..."]
                        
                        def add_rel_log(msg):
                            rel_logs.append(msg)
                            rel_log_area.code("\n".join(rel_logs), language="markdown")
                            
                        try:
                            # Topological sorting helper
                            def topo_sort(tbls, foreign_keys):
                                adj = {t: set() for t in tbls}
                                for fk in foreign_keys:
                                    t_from = fk['Table']
                                    t_to = fk['ForeignTable']
                                    if t_from in adj and t_to in adj and t_from != t_to:
                                        adj[t_from].add(t_to)
                                        
                                visited = set()
                                temp = set()
                                order = []
                                
                                def visit(node):
                                    if node in temp:
                                        return
                                    if node not in visited:
                                        temp.add(node)
                                        for dep in adj[node]:
                                            visit(dep)
                                        temp.remove(node)
                                        visited.add(node)
                                        order.append(node)
                                        
                                for t in tbls:
                                    visit(t)
                                return order
                                
                            def fb_type_to_grist(fb_type):
                                fb_type = str(fb_type).upper()
                                if fb_type in ["VARCHAR", "CHAR", "BLOB", "UNKNOWN"]:
                                    return "Text"
                                elif fb_type in ["SMALLINT", "INTEGER", "BIGINT"]:
                                    return "Int"
                                elif fb_type in ["FLOAT", "DOUBLE"]:
                                    return "Numeric"
                                elif fb_type in ["DATE", "TIMESTAMP", "TIME"]:
                                    return "DateTime"
                                return "Text"
                                
                            def clean_ref_col_name(col_id):
                                if col_id.lower().startswith('id_'):
                                    return "ref_" + col_id[3:]
                                return "ref_" + col_id

                            # Filter tables to only those that have a matching CSV file
                            active_tables = []
                            for t in verify_info["tables"]:
                                csv_file = os.path.join(verify_info["csv_dir"], f"{t.lower()}.csv")
                                if os.path.exists(csv_file):
                                    active_tables.append(t)
                                    
                            reviewed_fks_list = st.session_state.get("reviewed_fks", [])
                            ordered_tables = topo_sort(active_tables, reviewed_fks_list)
                            add_rel_log(f"📌 Ordem de importação calculada (apenas com CSVs): {' -> '.join(ordered_tables)}")
                            
                            # Map foreign keys by (Table, Column) -> ForeignTable
                            table_fks = {}
                            for fk in reviewed_fks_list:
                                table_fks[(fk['Table'], fk['Column'])] = fk['ForeignTable']
                                
                            # Phase 1: Create all tables with flat columns
                            add_rel_log("\n--- FASE 1: CRIANDO ESTRUTURAS (TABELAS E COLUNAS PLANAS) ---")
                            for table_id in ordered_tables:
                                add_rel_log(f"🛠️ Configurando tabela '{table_id}'...")
                                schema_payload = []
                                
                                # Read CSV data to detect decimal columns dynamically
                                df_data = None
                                csv_file = os.path.join(verify_info["csv_dir"], f"{table_id.lower()}.csv")
                                if os.path.exists(csv_file):
                                    try:
                                        df_data = pd.read_csv(csv_file)
                                    except:
                                        pass
                                
                                # Gather columns
                                cols = [c for c in verify_info["columns"] if c['Table'] == table_id]
                                for c in cols:
                                    col_id = c['Column']
                                    if col_id.upper() == 'ID':
                                        continue
                                        
                                    grist_type = fb_type_to_grist(c['Type'])
                                    
                                    # Detect float/decimal columns in CSV data to override Int to Numeric (including comma decimals)
                                    if df_data is not None and col_id in df_data.columns:
                                        series = df_data[col_id].dropna().astype(str)
                                        has_decimals = False
                                        for val in series:
                                            clean_val = val.replace(',', '.')
                                            try:
                                                float_val = float(clean_val)
                                                if float_val % 1 != 0:
                                                    has_decimals = True
                                                    break
                                            except ValueError:
                                                pass
                                        if has_decimals:
                                            grist_type = "Numeric"
                                                
                                    # Create foreign keys as simple Int or Text temporarily
                                    if (table_id, col_id) in table_fks:
                                        schema_payload.append({
                                            "id": col_id,
                                            "fields": {
                                                "label": col_id.replace('_', ' ').title(),
                                                "type": "Int" if grist_type == "Int" else "Text",
                                                "isFormula": False,
                                                "formula": ""
                                            }
                                        })
                                    else:
                                        schema_payload.append({
                                            "id": col_id,
                                            "fields": {
                                                "label": col_id.replace('_', ' ').title(),
                                                "type": grist_type,
                                                "isFormula": False,
                                                "formula": ""
                                            }
                                        })
                                        
                                ok, created_id = create_table(CURRENT_BASE_URL, AUTH_API_KEY, target_doc_id, table_id, schema_payload)
                                if ok:
                                    add_rel_log(f"   ✅ Tabela '{table_id}' criada.")
                                elif created_id == "EXISTING":
                                    add_rel_log(f"   ℹ️ Tabela '{table_id}' já existe no Grist.")
                                else:
                                    add_rel_log(f"   ❌ Erro ao criar tabela '{table_id}': {created_id}")
                                    
                            # Phase 2: Insert Data
                            add_rel_log("\n--- FASE 2: INSERINDO REGISTROS DOS ARQUIVOS CSV ---")
                            for table_id in ordered_tables:
                                csv_file = os.path.join(verify_info["csv_dir"], f"{table_id.lower()}.csv")
                                if not os.path.exists(csv_file):
                                    add_rel_log(f"   ⚠️ Arquivo CSV '{table_id.lower()}.csv' não encontrado, pulando carga de dados.")
                                    continue
                                    
                                if os.path.getsize(csv_file) <= 3:
                                    add_rel_log(f"   ℹ️ Tabela '{table_id}' está vazia (0 registros), pulando carga de dados.")
                                    continue
                                    
                                try:
                                    df = pd.read_csv(csv_file)
                                except Exception:
                                    add_rel_log(f"   ℹ️ Tabela '{table_id}' está vazia (0 registros), pulando carga de dados.")
                                    continue
                                    
                                add_rel_log(f"📂 Lendo {len(df)} registros para '{table_id}'...")
                                
                                records_to_insert = []
                                for idx, row in df.iterrows():
                                    fields_dict = {}
                                    rec_id = None
                                    for col in df.columns:
                                        val = row[col]
                                        if pd.isna(val):
                                            val = None
                                            
                                        if col.upper() == 'ID':
                                            rec_id = int(val) if val is not None else None
                                        else:
                                            if isinstance(val, str):
                                                # Convert legacy date formats to ISO
                                                if '/' in val:
                                                    try:
                                                        from datetime import datetime
                                                        # format: 24/10/2025 00:00:00 (19 chars)
                                                        if len(val) == 19 and val[2] == '/' and val[5] == '/' and val[10] == ' ':
                                                            dt = datetime.strptime(val, "%d/%m/%Y %H:%M:%S")
                                                            val = dt.strftime("%Y-%m-%d %H:%M:%S")
                                                        # format: 24/10/2025 (10 chars)
                                                        elif len(val) == 10 and val[2] == '/' and val[5] == '/':
                                                            dt = datetime.strptime(val, "%d/%m/%Y")
                                                            val = dt.strftime("%Y-%m-%d")
                                                    except ValueError:
                                                        pass
                                                
                                                if ',' in val:
                                                    try:
                                                        clean_val = val.replace(',', '.')
                                                        val = float(clean_val)
                                                    except ValueError:
                                                        pass
                                            fields_dict[col.upper()] = val
                                            
                                    records_to_insert.append({
                                        "id": rec_id,
                                        "fields": fields_dict
                                    })
                                    
                                scnt = 0
                                for i in range(0, len(records_to_insert), 500):
                                    batch = records_to_insert[i:i+500]
                                    ok, m = add_records(CURRENT_BASE_URL, AUTH_API_KEY, target_doc_id, table_id, batch)
                                    if ok:
                                        scnt += len(batch)
                                    else:
                                        add_rel_log(f"   ⚠️ Erro ao inserir lote na tabela '{table_id}': {m}")
                                add_rel_log(f"   ✅ {scnt}/{len(records_to_insert)} registros inseridos com sucesso.")
                                
                            # Helper to resolve string column names to Grist internal column refs
                            def resolve_visible_cols(base_url, api_key, doc_id):
                                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                                r_tables = requests.get(f"{base_url}/docs/{doc_id}/tables/_grist_Tables/records", headers=headers)
                                if r_tables.status_code != 200:
                                    return {}, {}
                                table_id_to_ref = {}
                                for rec in r_tables.json().get('records', []):
                                    fields = rec.get('fields', {})
                                    t_id = fields.get('tableId')
                                    if t_id:
                                        table_id_to_ref[t_id] = rec['id']
                                        
                                r_cols = requests.get(f"{base_url}/docs/{doc_id}/tables/_grist_Tables_column/records", headers=headers)
                                if r_cols.status_code != 200:
                                    return {}, {}
                                col_map = {}
                                for rec in r_cols.json().get('records', []):
                                    fields = rec.get('fields', {})
                                    t_ref = fields.get('parentId')
                                    c_id = fields.get('colId')
                                    if t_ref and c_id:
                                        col_map[(t_ref, c_id)] = rec['id']
                                        
                                return table_id_to_ref, col_map

                            # Phase 3: Connect Relationships (Native References)
                            add_rel_log("\n--- FASE 3: CONECTANDO RELACIONAMENTOS (REFERÊNCIAS NATIVAS) ---")
                            reviewed_fks_list = st.session_state.get("reviewed_fks", [])
                            
                            # 3.1: Create z_disp helper columns first for all tables with configured display columns
                            add_rel_log("⚙️ Criando colunas auxiliares de exibição (z_disp_*) para referências...")
                            for table_id in ordered_tables:
                                table_fks_list = [fk for fk in reviewed_fks_list if fk['Table'] == table_id]
                                if not table_fks_list:
                                    continue
                                    
                                new_helpers_payload = []
                                for fk in table_fks_list:
                                    col_id = fk['Column']
                                    target_table = fk['ForeignTable']
                                    display_col = fk.get('DisplayCol', 0)
                                    
                                    if target_table not in active_tables:
                                        continue
                                        
                                    if display_col and display_col != "0":
                                        helper_id = f"z_disp_{col_id}"
                                        new_helpers_payload.append({
                                            "id": helper_id,
                                            "fields": {
                                                "label": helper_id,
                                                "type": "Any",
                                                "isFormula": True,
                                                "formula": f"${col_id}.{display_col}"
                                            }
                                        })
                                
                                if new_helpers_payload:
                                    # Create columns (ignore if they already exist)
                                    ok_h, m_h = add_columns(CURRENT_BASE_URL, AUTH_API_KEY, target_doc_id, table_id, new_helpers_payload)
                                    if ok_h:
                                        add_rel_log(f"   ✅ Helpers criados para '{table_id}'")
                                    else:
                                        # It might fail if columns already exist, which is fine
                                        add_rel_log(f"   ℹ️ Helpers verificados/criados para '{table_id}'")
                            
                            # 3.2: Query current metadata column refs from Grist
                            add_rel_log("🔍 Resolvendo IDs numéricos das colunas no Grist...")
                            table_id_to_ref, col_map = resolve_visible_cols(CURRENT_BASE_URL, AUTH_API_KEY, target_doc_id)
                            
                            # 3.3: Convert columns to native References and set displayCol / visibleCol
                            for table_id in ordered_tables:
                                table_fks_list = [fk for fk in reviewed_fks_list if fk['Table'] == table_id]
                                if not table_fks_list:
                                    continue
                                    
                                add_rel_log(f"🔗 Convertendo colunas para referência nativa em '{table_id}'...")
                                ref_cols_payload = []
                                for fk in table_fks_list:
                                    col_id = fk['Column']
                                    target_table = fk['ForeignTable']
                                    display_col = fk.get('DisplayCol', 0)
                                    
                                    if target_table not in active_tables:
                                        add_rel_log(f"   ⚠️ Ignorando relação da coluna '{col_id}' para '{target_table}' pois a tabela de destino não foi importada.")
                                        continue
                                        
                                    numeric_visible_col = 0
                                    numeric_display_col = 0
                                    
                                    target_t_ref = table_id_to_ref.get(target_table)
                                    current_t_ref = table_id_to_ref.get(table_id)
                                    
                                    if display_col and display_col != "0" and target_t_ref and current_t_ref:
                                        numeric_visible_col = col_map.get((target_t_ref, display_col), 0)
                                        numeric_display_col = col_map.get((current_t_ref, f"z_disp_{col_id}"), 0)
                                        
                                    ref_cols_payload.append({
                                        "id": col_id,
                                        "fields": {
                                            "type": f"Ref:{target_table}",
                                            "visibleCol": numeric_visible_col,
                                            "displayCol": numeric_display_col
                                        }
                                    })
                                    
                                if ref_cols_payload:
                                    ok, m = update_columns(CURRENT_BASE_URL, AUTH_API_KEY, target_doc_id, table_id, ref_cols_payload)
                                    if ok:
                                        for rcol in ref_cols_payload:
                                            add_rel_log(f"   ✅ Coluna '{rcol['id']}' convertida com sucesso para '{rcol['fields']['type']}' (exibição: {rcol['fields']['visibleCol']})")
                                    else:
                                        add_rel_log(f"   ❌ Erro ao converter colunas em '{table_id}': {m}")
                                    
                            add_rel_log("\n🎉 IMPORTAÇÃO RELACIONAL TOTALMENTE CONCLUÍDA!")
                            st.success("Importação relacional finalizada com sucesso!")
                            st.balloons()
                        except Exception as ex:
                            st.error(f"Erro durante a importação relacional: {ex}")
                
                    st.divider()
                    st.subheader("🧹 Limpeza de Tabelas Vazias/Órfãs")
                    st.markdown("Se você já executou a importação antes e criou tabelas indesejadas (sem arquivos CSV), use este botão para apagá-las do documento do Grist.")
                    
                    if st.button("Limpar tabelas órfãs no Grist (sem CSV)", key="btn_clean_orphans"):
                        try:
                            # 1. Fetch tables in Grist doc
                            existing_tables = get_tables(CURRENT_BASE_URL, AUTH_API_KEY, target_doc_id)
                            existing_table_ids = [t['id'] for t in existing_tables if not t['id'].startswith('_grist')]
                            
                            # 2. Check which ones do NOT have matching CSVs in verify_info["csv_dir"]
                            to_delete = []
                            for t_id in existing_table_ids:
                                csv_file = os.path.join(verify_info["csv_dir"], f"{t_id.lower()}.csv")
                                if not os.path.exists(csv_file):
                                    to_delete.append(t_id)
                                    
                            if not to_delete:
                                st.info("Nenhuma tabela órfã encontrada no Grist.")
                            else:
                                st.write(f"🗑️ Deletando tabelas: {', '.join(to_delete)}")
                                ok_del, m_del = delete_tables_batch(CURRENT_BASE_URL, AUTH_API_KEY, target_doc_id, to_delete)
                                if ok_del:
                                    st.success(f"Tabelas removidas com sucesso: {', '.join(to_delete)}")
                                    try:
                                        st.rerun()
                                    except AttributeError:
                                        st.experimental_rerun()
                                else:
                                    st.error(f"Erro ao deletar tabelas: {m_del}")
                        except Exception as ex:
                            st.error(f"Erro ao limpar tabelas: {ex}")
                
                st.stop()
            
            # File Uploader
            uploaded_file = st.file_uploader(
                i18n[st.session_state.lang].get('import_upload_lbl', 'Selecione o arquivo CSV ou JSON'),
                type=["csv", "json"],
                key="import_file_uploader"
            )
            
            if uploaded_file is not None:
                # 2. Parse file and show preview
                file_name = uploaded_file.name
                is_csv = file_name.endswith('.csv')
                
                try:
                    if is_csv:
                        sep = st.text_input("Separador (CSV)", value=",")
                        df = pd.read_csv(uploaded_file, sep=sep)
                    else:
                        df = pd.read_json(uploaded_file)
                        
                    st.write(i18n[st.session_state.lang].get('import_preview', '🔍 Pré-visualização dos dados (Primeiras 5 linhas):'))
                    st.dataframe(df.head(5))
                    
                    # 3. Choose target Table
                    st.subheader(i18n[st.session_state.lang].get('import_table_settings', '⚙️ Configurações da Tabela'))
                    
                    existing_tables = get_tables(CURRENT_BASE_URL, AUTH_API_KEY, target_doc_id)
                    existing_table_ids = [t['id'] for t in existing_tables if not t['id'].startswith('_grist')]
                    
                    import_mode = st.radio(
                        i18n[st.session_state.lang].get('import_mode_lbl', 'Destino dos dados:'),
                        [
                            i18n[st.session_state.lang].get('import_mode_new', 'Criar nova tabela'),
                            i18n[st.session_state.lang].get('import_mode_existing', 'Adicionar a uma tabela existente')
                        ]
                    )
                    
                    if import_mode == i18n[st.session_state.lang].get('import_mode_new', 'Criar nova tabela'):
                        default_table_id = "".join([c if c.isalnum() or c == '_' else '_' for c in file_name.rsplit('.', 1)[0]])
                        while '__' in default_table_id:
                            default_table_id = default_table_id.replace('__', '_')
                        default_table_id = default_table_id.strip('_')
                        
                        target_table_id = st.text_input(
                            i18n[st.session_state.lang].get('import_new_table_id', 'ID da nova tabela (Apenas letras, números e _)'),
                            value=default_table_id
                        )
                        is_new_table = True
                    else:
                        target_table_id = st.selectbox(
                            i18n[st.session_state.lang].get('import_select_table', 'Selecione a tabela existente'),
                            options=sorted(existing_table_ids),
                            index=None
                        )
                        is_new_table = False
                        
                    if target_table_id:
                        # 4. Column settings and mapping
                        st.subheader(i18n[st.session_state.lang].get('import_cols_mapping', '📋 Mapeamento de Colunas'))
                        st.markdown(i18n[st.session_state.lang].get(
                            'import_cols_desc',
                            'Configure os tipos de coluna. Para colunas do tipo **Reference**, nós criaremos automaticamente uma coluna de link (Fórmula Lookup) no Grist!'
                        ))
                        
                        col_configs = []
                        for col in df.columns:
                            dtype = df[col].dtype
                            col_sanitized = "".join([c if c.isalnum() or c == '_' else '_' for c in col])
                            while '__' in col_sanitized:
                                col_sanitized = col_sanitized.replace('__', '_')
                            col_sanitized = col_sanitized.strip('_')
                            
                            st.write(f"---")
                            c1, c2, c3 = st.columns(3)
                            
                            with c1:
                                st.markdown(f"**{i18n[st.session_state.lang].get('lbl_source_col', 'Coluna de Origem')}:** `{col}` *(dtype: {dtype})*")
                                col_label = st.text_input(i18n[st.session_state.lang].get('lbl_dest_label', 'Label no Grist'), value=col, key=f"lbl_{col}")
                                col_id = st.text_input(i18n[st.session_state.lang].get('lbl_dest_id', 'ID da Coluna'), value=col_sanitized, key=f"id_{col}")
                                
                            # Heuristic for Reference auto-detection
                            detected_ref_table = None
                            col_lower = col.lower()
                            candidate_names = []
                            if col_lower.startswith('id_'):
                                candidate_names.append(col_lower[3:])
                            elif col_lower.endswith('_id'):
                                candidate_names.append(col_lower[:-3])
                            elif col_lower.startswith('id'):
                                candidate_names.append(col_lower[2:])
                            elif col_lower.endswith('id'):
                                candidate_names.append(col_lower[:-2])
                                
                            if candidate_names:
                                cand = candidate_names[0]
                                def normalize_name(name):
                                    return name.replace('_', '').replace(' ', '').lower().rstrip('s')
                                cand_norm = normalize_name(cand)
                                for t_id in existing_table_ids:
                                    t_id_norm = normalize_name(t_id)
                                    if cand_norm == t_id_norm:
                                        detected_ref_table = t_id
                                        break

                            # Suggest Bool if name matches boolean patterns or unique values are subset of {0, 1}
                            is_probably_bool = False
                            if col_lower.startswith('is_') or col_lower.startswith('has_') or col_lower.startswith('eh_') or col_lower.startswith('tem_'):
                                is_probably_bool = True
                            else:
                                try:
                                    unique_vals = set(df[col].dropna().unique())
                                    if len(unique_vals) > 0 and unique_vals.issubset({0, 1, 0.0, 1.0, '0', '1', 'True', 'False', True, False}):
                                        is_probably_bool = True
                                except:
                                    pass

                            with c2:
                                default_type_idx = 0 # Any
                                if detected_ref_table is not None:
                                    default_type_idx = 7 # Reference (Ref)
                                elif is_probably_bool:
                                    default_type_idx = 4 # Bool
                                elif pd.api.types.is_integer_dtype(dtype):
                                    default_type_idx = 2 # Int
                                elif pd.api.types.is_numeric_dtype(dtype):
                                    default_type_idx = 3 # Numeric
                                elif pd.api.types.is_bool_dtype(dtype):
                                    default_type_idx = 4 # Bool
                                elif 'date' in col.lower() or 'data' in col.lower():
                                    default_type_idx = 5 # Date
                                elif pd.api.types.is_string_dtype(dtype):
                                    default_type_idx = 1 # Text
                                    
                                col_type = st.selectbox(
                                    i18n[st.session_state.lang].get('lbl_grist_type', 'Tipo no Grist'),
                                    ["Any", "Text", "Int", "Numeric", "Bool", "Date", "Choice", "Reference (Ref)"],
                                    index=default_type_idx,
                                    key=f"type_{col}"
                                )
                                
                            with c3:
                                if col_type == "Reference (Ref)":
                                    sorted_tables = sorted(existing_table_ids)
                                    default_tbl_idx = None
                                    if detected_ref_table in sorted_tables:
                                        default_tbl_idx = sorted_tables.index(detected_ref_table)
                                        
                                    ref_table = st.selectbox(
                                        i18n[st.session_state.lang].get('lbl_ref_table', 'Tabela Referenciada'),
                                        options=sorted_tables,
                                        index=default_tbl_idx,
                                        key=f"reftbl_{col}"
                                    )
                                    if ref_table:
                                        ref_cols = get_columns(CURRENT_BASE_URL, AUTH_API_KEY, target_doc_id, ref_table)
                                        ref_col_ids = ['id'] + [rc['id'] for rc in ref_cols if rc['id'].lower() != 'id']
                                        
                                        default_match_idx = 0
                                        match_col = st.selectbox(
                                            i18n[st.session_state.lang].get('lbl_match_col', 'Coluna de Match'),
                                            options=ref_col_ids,
                                            index=default_match_idx,
                                            key=f"matchcol_{col}"
                                        )
                                    else:
                                        match_col = None
                                else:
                                    ref_table = None
                                    match_col = None
                                    
                            col_configs.append({
                                "source_col": col,
                                "id": col_id,
                                "label": col_label,
                                "type": col_type,
                                "ref_table": ref_table,
                                "match_col": match_col
                            })
                            
                        st.write("---")
                        
                        # Helpers for data cleaning
                        def clean_bool(val):
                            if pd.isna(val) or val is None:
                                return None
                            if isinstance(val, str):
                                v = val.strip().lower()
                                if v in ('1', 'true', 'yes', 't', 'y', 's', 'sim'):
                                    return True
                                if v in ('0', 'false', 'no', 'f', 'n', 'não'):
                                    return False
                            elif isinstance(val, (int, float)):
                                return bool(val)
                            return bool(val)

                        def clean_date(val):
                            if pd.isna(val) or val is None or str(val).strip() == "":
                                return None
                            try:
                                if hasattr(val, 'strftime'):
                                    return val.strftime('%Y-%m-%d')
                                parsed = pd.to_datetime(val)
                                return parsed.strftime('%Y-%m-%d')
                            except:
                                return str(val)
                                
                        def make_ref_column_name(col_id):
                            ref_id = col_id
                            if ref_id.lower().startswith('id_'):
                                ref_id = ref_id[3:]
                            elif ref_id.lower().endswith('_id'):
                                ref_id = ref_id[:-3]
                            elif ref_id.lower().startswith('id'):
                                ref_id = ref_id[2:]
                            elif ref_id.lower().endswith('id'):
                                ref_id = ref_id[:-2]
                            if ref_id == col_id:
                                ref_id = f"ref_{col_id}"
                            ref_id = ref_id.strip('_')
                            return ref_id if ref_id else f"ref_{col_id}"
                        
                        if st.button(i18n[st.session_state.lang].get('btn_import_start', 'Iniciar Importação'), type="primary", key="btn_trigger_import"):
                            st.session_state.import_logs = ["📥 Iniciando processo de importação..."]
                            log_area = st.empty()
                            
                            def add_import_log(msg):
                                st.session_state.import_logs.append(msg)
                                log_area.code("\n".join(st.session_state.import_logs), language="markdown")
                            
                            table_created = True
                            ref_formulas_to_add = []
                            
                            if is_new_table:
                                add_import_log(f"🛠️ Criando nova tabela '{target_table_id}'...")
                                schema_payload = []
                                
                                for cfg in col_configs:
                                    if cfg["id"].lower() == 'id':
                                        continue
                                        
                                    fields = {
                                        "label": cfg["label"],
                                        "isFormula": False,
                                        "formula": ""
                                    }
                                    
                                    if cfg["type"] == "Reference (Ref)":
                                        fields["type"] = "Int" if pd.api.types.is_integer_dtype(df[cfg["source_col"]].dtype) else "Text"
                                        schema_payload.append({
                                            "id": cfg["id"],
                                            "fields": fields
                                        })
                                        
                                        ref_col_id = make_ref_column_name(cfg["id"])
                                        ref_fields = {
                                            "label": make_ref_column_name(cfg["label"]).replace('_', ' ').title(),
                                            "type": f"Ref:{cfg['ref_table']}",
                                            "isFormula": True,
                                            "formula": f"{cfg['ref_table']}.lookupOne({cfg['match_col']}=${cfg['id']})"
                                        }
                                        ref_formulas_to_add.append({
                                            "id": ref_col_id,
                                            "fields": ref_fields
                                        })
                                    else:
                                        fields["type"] = cfg["type"]
                                        schema_payload.append({
                                            "id": cfg["id"],
                                            "fields": fields
                                        })
                                        
                                ok, created_id = create_table(CURRENT_BASE_URL, AUTH_API_KEY, target_doc_id, target_table_id, schema_payload)
                                if ok:
                                    add_import_log(f"   ✅ Tabela '{created_id}' criada com sucesso!")
                                    target_table_id = created_id
                                else:
                                    add_import_log(f"   ❌ Erro ao criar tabela: {created_id}")
                                    table_created = False
                            else:
                                add_import_log(f"   ℹ️ Usando tabela existente '{target_table_id}'.")
                            
                            if table_created:
                                add_import_log(f"➤ Preparando dados para inserção...")
                                records_to_insert = []
                                
                                for idx, row in df.iterrows():
                                    fields_dict = {}
                                    rec_id = None
                                    for cfg in col_configs:
                                        val = row[cfg["source_col"]]
                                        
                                        if pd.isna(val):
                                            val = None
                                        elif cfg["type"] == "Bool":
                                            val = clean_bool(val)
                                        elif cfg["type"] == "Int" and val is not None:
                                            try: val = int(float(str(val)))
                                            except: pass
                                        elif cfg["type"] == "Numeric" and val is not None:
                                            try: val = float(val)
                                            except: pass
                                        elif cfg["type"] == "Date" and val is not None:
                                            val = clean_date(val)
                                            
                                        if cfg["id"].lower() == 'id':
                                            try: rec_id = int(float(str(val)))
                                            except: pass
                                        else:
                                            fields_dict[cfg["id"]] = val
                                            
                                    rec_payload = {"fields": fields_dict}
                                    if rec_id is not None:
                                        rec_payload["id"] = rec_id
                                    records_to_insert.append(rec_payload)
                                    
                                add_import_log(f"➤ Inserindo {len(records_to_insert)} registros...")
                                scnt = 0
                                for i in range(0, len(records_to_insert), 500):
                                    batch = records_to_insert[i:i+500]
                                    ok, m = add_records(CURRENT_BASE_URL, AUTH_API_KEY, target_doc_id, target_table_id, batch)
                                    if ok:
                                        scnt += len(batch)
                                        add_import_log(f"   ✅ {scnt}/{len(records_to_insert)} registros inseridos.")
                                    else:
                                        add_import_log(f"   ⚠️ Lote com erro: {m}")
                                        
                                if ref_formulas_to_add:
                                    add_import_log(f"➤ Criando {len(ref_formulas_to_add)} colunas de Referência Inteligentes...")
                                    ok_add, m_add = add_columns(CURRENT_BASE_URL, AUTH_API_KEY, target_doc_id, target_table_id, ref_formulas_to_add)
                                    if ok_add:
                                        for rcol in ref_formulas_to_add:
                                            add_import_log(f"   ✅ Coluna '{rcol['id']}' configurada com fórmula: `{rcol['fields']['formula']}`")
                                    else:
                                        add_import_log(f"   ❌ Erro ao adicionar colunas de referência: {m_add}")
                                        
                                add_import_log(f"\n🎉 IMPORTAÇÃO TOTALMENTE CONCLUÍDA!")
                                st.success(i18n[st.session_state.lang].get('toast_import_ok', 'Importação Concluída!'))
                                st.balloons()
                                
                except Exception as e:
                    st.error(f"Erro ao ler arquivo: {e}")
                    
        else:
            st.info("Mapeamento necessário.")

    with tab6:
        st.header(i18n[st.session_state.lang]["header_audit"])
        render_help_icon("audit")
        configs = load_audit_configs()
        sel_c = st.selectbox(i18n[st.session_state.lang]["load_config"], [i18n[st.session_state.lang]["new_config"]] + list(configs.keys()))
        st.divider()
        if st.session_state.mapped_data is not None:
            all_a = st.session_state.mapped_data[['Documento', 'Doc ID']].drop_duplicates()
            doc_opts_a = {r['Documento']: r['Doc ID'] for _, r in all_a.iterrows()}
            def_idx = next((i for i, k in enumerate(sorted(doc_opts_a.keys())) if doc_opts_a[k] == configs.get(sel_c,{}).get('doc_id')), None)
            sel_d = st.selectbox(i18n[st.session_state.lang]["target_doc"], sorted(doc_opts_a.keys()), index=def_idx)
            if sel_d:
                did = doc_opts_a[sel_d]
                tables = get_tables(CURRENT_BASE_URL, AUTH_API_KEY, did)
                t_opts = {t['id']: t['id'] for t in tables}
                def_t_idx = next((i for i, k in enumerate(sorted(t_opts.keys())) if k == configs.get(sel_c,{}).get('table_id')), None)
                sel_t = st.selectbox(i18n[st.session_state.lang]["ref_table"], sorted(t_opts.keys()), index=def_t_idx)
                if sel_t:
                    cols = get_columns(CURRENT_BASE_URL, AUTH_API_KEY, did, sel_t)
                    c_opts = {c['id']: c['fields']['label'] for c in cols}
                    sorted_l = sorted(c_opts.values())
                    def_ti = next((i for i, l in enumerate(sorted_l) if c_opts.get(configs.get(sel_c,{}).get('title_col')) == l), None)
                    def_em = [c_opts[eid] for eid in configs.get(sel_c,{}).get('email_cols', []) if eid in c_opts]
                    c1, c2 = st.columns(2)
                    s_title = c1.selectbox(i18n[st.session_state.lang]['lbl_col_title'], sorted_l, index=def_ti)
                    s_emails = c2.multiselect(i18n[st.session_state.lang]['lbl_col_email'], sorted_l, default=def_em)
                    if st.button(i18n[st.session_state.lang]["btn_audit"]):
                        with st.spinner("Cruzando..."):
                            tid_col = next(k for k,v in c_opts.items() if v == s_title)
                            eid_cols = [k for k,v in c_opts.items() if v in s_emails]
                            doc_u = get_doc_users(CURRENT_BASE_URL, AUTH_API_KEY, did)
                            act_m = {u['email'].strip().lower(): u.get('access') for u in doc_u if u.get('email')}
                            recs, err_a = fetch_table_records(CURRENT_BASE_URL, AUTH_API_KEY, did, sel_t)
                            t_data, matched = [], set()
                            for r in recs:
                                f = r['fields']
                                row = {s_title: str(f.get(tid_col, ""))}
                                miss = []
                                for cid in eid_cols:
                                    val = f.get(cid)
                                    cl = []
                                    list_e = [val] if isinstance(val, str) else (val[1:] if isinstance(val, list) and val and val[0] == 'L' else (val if isinstance(val, list) else []))
                                    for e in list_e:
                                        if not isinstance(e, str): continue
                                        em = e.strip().lower()
                                        if em in act_m: cl.append(f"✅ {em}"); matched.add(em)
                                        else: cl.append(f"🔴 {em}"); miss.append(em)
                                    row[c_opts[cid]] = "\n".join(cl)
                                row["_miss"] = json.dumps(miss); row["_type"] = "ref"; t_data.append(row)
                            all_e = set(act_m.keys())
                            for orph in sorted(list(all_e - matched)):
                                t_data.append({s_title: "", s_emails[0]: f"☢️ {orph}", "_miss": "[]", "_orph": orph, "_type": "orph"})
                            if t_data:
                                df_res = pd.DataFrame(t_data); df_res.insert(0, "Selecionar", False)
                                edited = st.data_editor(df_res, column_order=["Selecionar", s_title] + s_emails, use_container_width=True, hide_index=True)
                                sel_r = edited[edited["Selecionar"]]
                                if not sel_r.empty:
                                    tg, tr = [], []
                                    for _, row in sel_r.iterrows():
                                        if row["_type"] == "ref": tg.extend(json.loads(row["_miss"]))
                                        elif row["_type"] == "orph": tr.append(row["_orph"])
                                    if tg and st.button(i18n[st.session_state.lang]["btn_grant"]):
                                        for e in set(tg): update_doc_access(CURRENT_BASE_URL, AUTH_API_KEY, did, e, "viewers")
                                        st.success(i18n[st.session_state.lang]["msg_ok"]); time.sleep(1); st.rerun()
                                    if tr and st.button(i18n[st.session_state.lang]["btn_remove"]):
                                        for e in set(tr): update_doc_access(CURRENT_BASE_URL, AUTH_API_KEY, did, e, None)
                                        st.success(i18n[st.session_state.lang]["msg_ok"]); time.sleep(1); st.rerun()
        else: st.info("Mapeamento necessário.")

    with tab8:
        st.header(i18n[st.session_state.lang]["header_blueprint"])
        render_help_icon("blueprint")
        st.subheader(i18n[st.session_state.lang]["new_doc_section"])
        c1, c2 = st.columns([2, 1])
        n_doc = c1.text_input(i18n[st.session_state.lang]['doc_name'])
        wss = get_workspaces_and_docs(CURRENT_BASE_URL, AUTH_API_KEY, selected_org_id)
        ws_opts = {ws['name']: ws['id'] for ws in wss}
        s_ws = c2.selectbox(i18n[st.session_state.lang]['lbl_workspace'], sorted(ws_opts.keys()))
        if st.button(i18n[st.session_state.lang]["btn_create"]):
            if n_doc: ok, res = create_document(CURRENT_BASE_URL, AUTH_API_KEY, ws_opts[s_ws], n_doc); st.success(i18n[st.session_state.lang]["success_created"].format(res=res)); st.session_state.last_id = res; st.cache_data.clear()
        st.divider(); st.subheader(i18n[st.session_state.lang]["apply_structure_section"])
        # Fetch LIVE docs directly from Grist API to prevent cached ID disasters
        wss_live = get_workspaces_and_docs(CURRENT_BASE_URL, AUTH_API_KEY, selected_org_id)
        opts_b = {d['name']: d['id'] for ws in wss_live for d in ws.get('docs', [])}
        
        if 'last_id' in st.session_state: opts_b[i18n[st.session_state.lang]['newly_created']] = st.session_state.last_id
        target_b = st.selectbox(i18n[st.session_state.lang]["target_doc"], sorted(opts_b.keys(), reverse=True))
        ovw = st.checkbox(i18n[st.session_state.lang]["overwrite_warning"])
        
        if st.button(i18n[st.session_state.lang]["btn_gen_json"]):
             tid = opts_b[target_b]
             tables = get_tables(CURRENT_BASE_URL, AUTH_API_KEY, tid)
             blueprint = []
             for t in tables:
                 if t['id'].startswith('_grist'): continue
                 cols = get_columns(CURRENT_BASE_URL, AUTH_API_KEY, tid, t['id'])
                 blueprint.append({
                     "id": t['id'],
                     "columns": [{"id": c['id'], "label": c['fields'].get('label'), "type": c['fields'].get('type'), "isFormula": c['fields'].get('isFormula'), "formula": c['fields'].get('formula')} for c in cols if c['id'] != 'manualSort']
                 })
             st.session_state.blueprint_editor_area = json.dumps(blueprint, indent=2, ensure_ascii=False)

        js_raw = st.text_area(i18n[st.session_state.lang]["blueprint_json"], key="blueprint_editor_area", height=400)
        
        if target_b:
            st.warning(i18n[st.session_state.lang]["warning_mod_doc"].format(target_b=target_b, CURRENT_BASE_URL=CURRENT_BASE_URL))
            confirm_exec = st.checkbox(i18n[st.session_state.lang]["confirm_exec_checkbox"])
            
            if st.button(i18n[st.session_state.lang]["btn_exec"], disabled=not confirm_exec):
                if not js_raw.strip() and not ovw: 
                    st.error(i18n[st.session_state.lang]["err_empty_json_overwrite"])
                else:
                    try:
                        tid = opts_b[target_b]
                        data = []
                        if js_raw.strip():
                            data = json.loads(js_raw)
                            
                        if ovw:
                            ex = get_tables_no_cache(CURRENT_BASE_URL, AUTH_API_KEY, tid)
                            tables_to_delete = [t['id'] for t in ex if not t['id'].startswith('_grist')]
                            if tables_to_delete:
                                # Pre-pass: Lobotomy (Convert all columns to empty Text to kill formulas before deleting tables)
                                st.info(i18n[st.session_state.lang]["info_disable_formulas"])
                                for del_tid in tables_to_delete:
                                    try:
                                        cols = get_columns_no_cache(CURRENT_BASE_URL, AUTH_API_KEY, tid, del_tid)
                                        lobotomy_payload = []
                                        for c in cols:
                                            # We just change the type and strip formulas so the Sandbox doesn't crash on deletion
                                            if c['id'] != 'manualSort':
                                                lobotomy_payload.append({"id": c['id'], "fields": {"type": "Text", "isFormula": False, "formula": ""}})
                                        if lobotomy_payload:
                                            update_columns(CURRENT_BASE_URL, AUTH_API_KEY, tid, del_tid, lobotomy_payload)
                                    except:
                                        pass # If we can't lobotomize, we just ignore and try the deletion anyway
                                
                                ok_del, m_del = delete_tables_batch(CURRENT_BASE_URL, AUTH_API_KEY, tid, tables_to_delete)
                                if not ok_del:
                                    st.error(i18n[st.session_state.lang]["err_clean_doc"].format(m_del=m_del))
                                    raise Exception("Falha na limpeza.")
                                else:
                                    st.success(i18n[st.session_state.lang]["success_clean_doc"].format(count=len(tables_to_delete)))
                                    time.sleep(1)
                            else:
                                st.info(i18n[st.session_state.lang]["info_no_user_tables_clean"])
                                
                        if not data:
                            st.success(i18n[st.session_state.lang]["success_clean_only"])
                        else:
                            # Phase 1: Tables & Non-Ref cols
                            for tbl in data:
                                t_id = tbl['id']
                                cols = [{"id": c['id'], "fields": {"label": c.get('label', c['id']), "type": c.get('type', 'Text'), "isFormula": c.get('isFormula', False), "formula": c.get('formula', '')}} for c in tbl.get('columns', []) if not str(c.get('type','')).startswith('Ref:')]
                                ok, m = create_table(CURRENT_BASE_URL, AUTH_API_KEY, tid, t_id, cols)
                                if m == "EXISTING": add_columns(CURRENT_BASE_URL, AUTH_API_KEY, tid, t_id, cols)
                            time.sleep(0.5)
                            # Phase 2: Ref cols
                            for tbl in data:
                                t_id = tbl['id']
                                refs = [{"id": c['id'], "fields": {"label": c.get('label', c['id']), "type": c.get('type'), "isFormula": c.get('isFormula', False), "formula": c.get('formula', '')}} for c in tbl.get('columns', []) if str(c.get('type','')).startswith('Ref:')]
                                if refs: add_columns(CURRENT_BASE_URL, AUTH_API_KEY, tid, t_id, refs)
                            st.success(i18n[st.session_state.lang]["success_blueprint"])
                    except Exception as e: st.error(i18n[st.session_state.lang]["err_generic"].format(e=e))

    with tab10:
        st.header(i18n[st.session_state.lang]["header_ai"])
        render_help_icon("ai")
        opts_ia = {r['Documento']: r['Doc ID'] for _, r in st.session_state.mapped_data[['Documento', 'Doc ID']].drop_duplicates().iterrows()} if st.session_state.mapped_data is not None else {d['name']: d['id'] for ws in wss for d in ws.get('docs', [])}
        sel_ia = st.selectbox(i18n[st.session_state.lang]["target_doc"], sorted(opts_ia.keys()), index=None, key="ia_doc")
        if sel_ia:
            did = opts_ia[sel_ia]
            tbls = get_tables(CURRENT_BASE_URL, AUTH_API_KEY, did)
            sel_t = st.multiselect(i18n[st.session_state.lang]["lbl_tables"], sorted([t['id'] for t in tbls if not t['id'].startswith('_grist')]))
            if sel_t and st.button(i18n[st.session_state.lang]["btn_gen_template"]):
                tpl = []
                for tid in sel_t:
                    cols = get_columns(CURRENT_BASE_URL, AUTH_API_KEY, did, tid)
                    # Try to fetch some sample records
                    recs, err = fetch_table_records(CURRENT_BASE_URL, AUTH_API_KEY, did, tid)
                    sample_recs = []
                    if recs:
                        for r in recs[:3]: # 3 samples
                             sample_recs.append({k: v for k, v in r['fields'].items() if not k.startswith('gristHelper')})
                    
                    if not sample_recs:
                        sample_recs = [{c['id']: "..." for c in cols if not c['fields'].get('isFormula')}]
                        
                    tpl.append({"table_id": tid, "records": sample_recs})
                st.session_state.ia_tpl = json.dumps(tpl, indent=2, ensure_ascii=False)
            if getattr(st.session_state, 'ia_tpl', None):
                st.text_area(i18n[st.session_state.lang]["lbl_ai_template"], st.session_state.ia_tpl, height=200)
                inp = st.text_area(i18n[st.session_state.lang]["lbl_paste_ai"])
                if st.button(i18n[st.session_state.lang]["btn_populate"]):
                    try:
                        for item in json.loads(inp): add_records(CURRENT_BASE_URL, AUTH_API_KEY, did, item['table_id'], item['records'])
                        st.success(i18n[st.session_state.lang]["msg_ok"]); st.balloons()
                    except Exception as e: st.error(i18n[st.session_state.lang]["err_generic"].format(e=e))

elif main_menu_key == 'limits':
    st.header(i18n[st.session_state.lang]['tab_limits'])
    render_help_icon("limits")
    if st.session_state.mapped_data is not None:
        docs = st.session_state.mapped_data[['Documento', 'Doc ID', 'Workspace']].drop_duplicates()
    else:
        wss = get_workspaces_and_docs(CURRENT_BASE_URL, AUTH_API_KEY, selected_org_id)
        docs = pd.DataFrame([{'Documento': d['name'], 'Doc ID': d['id'], 'Workspace': ws['name']} for ws in wss for d in ws.get('docs', [])])
    if st.button(i18n[st.session_state.lang]["btn_scan_limits"]):
        res = []
        for _, r in docs.iterrows():
            size = get_real_data_size(CURRENT_BASE_URL, AUTH_API_KEY, r['Doc ID'])
            usage, _ = get_doc_usage(CURRENT_BASE_URL, AUTH_API_KEY, r['Doc ID'])
            rows = usage.get('rowCount', {}).get('total', 0) if usage else 0
            res.append({'Documento': r['Documento'], 'Linhas (%)': round(rows/5000*100, 1), 'Dados (%)': round(size/(10*1024*1024)*100, 1), 'Total Linhas': rows})
        st.session_state.usage_df = pd.DataFrame(res)
    if getattr(st.session_state, 'usage_df', None) is not None:
        st.dataframe(st.session_state.usage_df, use_container_width=True, hide_index=True, column_config={"Linhas (%)": st.column_config.ProgressColumn(min_value=0, max_value=100), "Dados (%)": st.column_config.ProgressColumn(min_value=0, max_value=100)})

elif main_menu_key == 'help':
    st.header(i18n[st.session_state.lang]["header_help"])
    st.markdown(i18n[st.session_state.lang]["help_markdown"], unsafe_allow_html=True)
