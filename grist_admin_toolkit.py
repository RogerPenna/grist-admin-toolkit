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
        'sidebar_version': '**Version: 1.0**',
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
        'help_markdown': '<div id="help-top"></div>\n\n# 📖 Comprehensive User Guide\n\nWelcome to the **Grist Admin & Data Toolkit**. This application is designed for power users and administrators to manage complex Grist organizations, audit security at scale, and perform advanced data engineering tasks.\n\n<a name="sidebar"></a>\n## 🧭 Sidebar & Navigation\nThe sidebar is your command center. \n- **Connection:** You can connect to the standard Grist SaaS (`docs.getgrist.com`) or any self-hosted instance. When adding a custom server, provide the full API URL (e.g., `https://grist.example.com/api`).\n- **API Key:** Requires a valid API Key with **Owner** permissions for the tasks you intend to perform.\n- **Organization:** Switching the organization updates the scope of all tabs. Most tools will only "see" documents within the selected organization.\n- **Full Reload:** Clears the local cache and forces a fresh fetch of organizations and workspaces from the server.\n\n---\n\n# 🔐 Access Management\n\n<a name="global-view"></a>\n### 👥 Global View\nThis tab shows users who are members of the **Team Site** (Organization level).\n- **User List:** Displays the primary email, display name, and their organization-wide role (Viewer, Editor, Admin).\n- **User Details (Deep Audit):** If you have performed a scan in the **Mapping** tab, you can select a user here to see every individual document they have **direct** access to. This is essential for identifying "permission creep" where a user has more access than their global role suggests.\n\n<a name="mapping"></a>\n### 🗺️ Document Mapping\nThe Mapping engine performs a recursive security audit. It iterates through every workspace and every document in the organization, calling the Grist Access API for each.\n- **Scanning:** Since this involves many API calls, it can take a few minutes for large organizations. \n- **Cache:** Results are stored in `mapping_cache.json` to allow you to work across sessions without re-scanning.\n- **Filtering:** Use the filters to find specific users or documents. The "Hide Inherited" option is crucial—it filters out users who have access simply because they are part of a workspace, showing you only those with explicitly granted document-level permissions.\n- **Bulk Operations:** Select multiple users/documents and use the **Operations** panel to:\n    - **Copy Permissions:** Replicate a set of users and their roles from one document to another.\n    - **Update Roles:** Change the access level (e.g., Viewer to Editor) for all selected rows at once.\n\n<a name="quick-actions"></a>\n### ⚡ Quick Actions\nDesigned for speed. If you have a list of 50 emails that need to be added to a specific project document immediately, this is the tool.\n- **Add/Remove:** Paste a list of emails (comma, space, or newline separated). The tool will normalize the emails (lowercase, trim) and apply the requested role.\n\n<a name="acl"></a>\n### 🛡️ Access Rules (ACL)\nGrist\'s internal `_grist_ACLRules` and `_grist_ACLResources` tables are notoriously difficult to read. This tool **denormalizes** them into a human-readable grid.\n- **View:** See which tables and columns are protected and by what formula.\n- **Edit:** For advanced users, you can paste a JSON structure to completely redefine the rules. \n- **Safety:** Every time you apply new rules, the tool automatically saves a timestamped JSON backup in the `/backups` folder. If you break the Sandbox, you can restore from these files.\n\n---\n\n# 🏗️ Data Engineering\n\n<a name="cloner"></a>\n### 🏗️ Table Cloner\nCopies the **Schema** (structure) of a table from a source document to one or more target documents.\n- It copies column IDs, Labels, Types, Formulas, and Widget Options.\n- **Note:** It does **not** move the data (rows), only the structure. Ideal for creating templates.\n\n<a name="transporter"></a>\n### 🚚 Data Transporter\nA sophisticated 3-phase engine to move entire datasets between documents while preserving relationships and formulas.\n- **Phase 1 (Structure):** Creates the tables. To prevent "Sandbox Errors" caused by circular references (e.g., Table A refers to B, and B refers to A), it initially creates all Reference columns as "Any" type.\n- **Phase 2 (Data):** Transfers all records in batches of 500. Reference IDs (Row IDs) are preserved.\n- **Phase 3 (Formulas):** The "Intelligence" phase. It updates the columns to their final types, restores the `visibleCol` mapping (the column shown in the dropdown), and re-activates Python formulas.\n\n<a name="audit"></a>\n### ⚖️ Integrity Audit\nThis is a specialized "Sync" tool. It compares a **Control Table** (a table inside Grist where you manage who *should* have access) with **Actual Grist Permissions**.\n- **Missing (🔴):** Users who are in your table but don\'t actually have access to the document. Use "Grant" to fix this.\n- **Orphan (☢️):** Users who have access to the document but are NOT in your control table. Use "Remove" to revoke unauthorized access.\n\n<a name="blueprint"></a>\n### 🛠️ Blueprint (JSON)\nEnables "Infrastructure as Code" for Grist.\n- **Wipe & Rebuild:** If "Overwrite" is checked, the tool performs a **"Lobotomy"**: it first converts all columns in the document to plain text (removing formulas) to ensure the Grist Sandbox doesn\'t crash during table deletion. It then deletes all tables and rebuilds the document from your JSON blueprint.\n\n<a name="ai"></a>\n### 📥 Populate with AI\nBridge the gap between LLMs and Grist.\n- **Template:** Generates a JSON structure of your table with "..." placeholders.\n- **Workflow:** Paste this template into ChatGPT/Claude with a prompt like "Fill this with 20 realistic rows of project data". Paste the AI response back into the tool to populate your table instantly.\n\n---\n\n# ⚙️ System\n\n<a name="limits"></a>\n### 📊 Limits & Usage\nGrist documents perform best when kept under certain row counts and file sizes.\n- **Scan Limits:** Calculates usage percentages for every document in the organization.\n- **Linhas (%):** Based on the standard 5,000 row "soft limit" for optimal performance.\n- **Dados (%):** Based on a 10MB SQLite file size limit. Helps you identify docs that need optimization or history clearing.',
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
        'sidebar_version': '**Version: 1.0**',
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
        'help_markdown': '<div id="help-top"></div>\n\n# 📖 Comprehensive User Guide\n\nWelcome to the **Grist Admin & Data Toolkit**. This application is designed for power users and administrators to manage complex Grist organizations, audit security at scale, and perform advanced data engineering tasks.\n\n<a name="sidebar"></a>\n## 🧭 Sidebar & Navigation\nThe sidebar is your command center. \n- **Connection:** You can connect to the standard Grist SaaS (`docs.getgrist.com`) or any self-hosted instance. When adding a custom server, provide the full API URL (e.g., `https://grist.example.com/api`).\n- **API Key:** Requires a valid API Key with **Owner** permissions for the tasks you intend to perform.\n- **Organization:** Switching the organization updates the scope of all tabs. Most tools will only "see" documents within the selected organization.\n- **Full Reload:** Clears the local cache and forces a fresh fetch of organizations and workspaces from the server.\n\n---\n\n# 🔐 Access Management\n\n<a name="global-view"></a>\n### 👥 Global View\nThis tab shows users who are members of the **Team Site** (Organization level).\n- **User List:** Displays the primary email, display name, and their organization-wide role (Viewer, Editor, Admin).\n- **User Details (Deep Audit):** If you have performed a scan in the **Mapping** tab, you can select a user here to see every individual document they have **direct** access to. This is essential for identifying "permission creep" where a user has more access than their global role suggests.\n\n<a name="mapping"></a>\n### 🗺️ Document Mapping\nThe Mapping engine performs a recursive security audit. It iterates through every workspace and every document in the organization, calling the Grist Access API for each.\n- **Scanning:** Since this involves many API calls, it can take a few minutes for large organizations. \n- **Cache:** Results are stored in `mapping_cache.json` to allow you to work across sessions without re-scanning.\n- **Filtering:** Use the filters to find specific users or documents. The "Hide Inherited" option is crucial—it filters out users who have access simply because they are part of a workspace, showing you only those with explicitly granted document-level permissions.\n- **Bulk Operations:** Select multiple users/documents and use the **Operations** panel to:\n    - **Copy Permissions:** Replicate a set of users and their roles from one document to another.\n    - **Update Roles:** Change the access level (e.g., Viewer to Editor) for all selected rows at once.\n\n<a name="quick-actions"></a>\n### ⚡ Quick Actions\nDesigned for speed. If you have a list of 50 emails that need to be added to a specific project document immediately, this is the tool.\n- **Add/Remove:** Paste a list of emails (comma, space, or newline separated). The tool will normalize the emails (lowercase, trim) and apply the requested role.\n\n<a name="acl"></a>\n### 🛡️ Access Rules (ACL)\nGrist\'s internal `_grist_ACLRules` and `_grist_ACLResources` tables are notoriously difficult to read. This tool **denormalizes** them into a human-readable grid.\n- **View:** See which tables and columns are protected and by what formula.\n- **Edit:** For advanced users, you can paste a JSON structure to completely redefine the rules. \n- **Safety:** Every time you apply new rules, the tool automatically saves a timestamped JSON backup in the `/backups` folder. If you break the Sandbox, you can restore from these files.\n\n---\n\n# 🏗️ Data Engineering\n\n<a name="cloner"></a>\n### 🏗️ Table Cloner\nCopies the **Schema** (structure) of a table from a source document to one or more target documents.\n- It copies column IDs, Labels, Types, Formulas, and Widget Options.\n- **Note:** It does **not** move the data (rows), only the structure. Ideal for creating templates.\n\n<a name="transporter"></a>\n### 🚚 Data Transporter\nA sophisticated 3-phase engine to move entire datasets between documents while preserving relationships and formulas.\n- **Phase 1 (Structure):** Creates the tables. To prevent "Sandbox Errors" caused by circular references (e.g., Table A refers to B, and B refers to A), it initially creates all Reference columns as "Any" type.\n- **Phase 2 (Data):** Transfers all records in batches of 500. Reference IDs (Row IDs) are preserved.\n- **Phase 3 (Formulas):** The "Intelligence" phase. It updates the columns to their final types, restores the `visibleCol` mapping (the column shown in the dropdown), and re-activates Python formulas.\n\n<a name="audit"></a>\n### ⚖️ Integrity Audit\nThis is a specialized "Sync" tool. It compares a **Control Table** (a table inside Grist where you manage who *should* have access) with **Actual Grist Permissions**.\n- **Missing (🔴):** Users who are in your table but don\'t actually have access to the document. Use "Grant" to fix this.\n- **Orphan (☢️):** Users who have access to the document but are NOT in your control table. Use "Remove" to revoke unauthorized access.\n\n<a name="blueprint"></a>\n### 🛠️ Blueprint (JSON)\nEnables "Infrastructure as Code" for Grist.\n- **Wipe & Rebuild:** If "Overwrite" is checked, the tool performs a **"Lobotomy"**: it first converts all columns in the document to plain text (removing formulas) to ensure the Grist Sandbox doesn\'t crash during table deletion. It then deletes all tables and rebuilds the document from your JSON blueprint.\n\n<a name="ai"></a>\n### 📥 Populate with AI\nBridge the gap between LLMs and Grist.\n- **Template:** Generates a JSON structure of your table with "..." placeholders.\n- **Workflow:** Paste this template into ChatGPT/Claude with a prompt like "Fill this with 20 realistic rows of project data". Paste the AI response back into the tool to populate your table instantly.\n\n---\n\n# ⚙️ System\n\n<a name="limits"></a>\n### 📊 Limits & Usage\nGrist documents perform best when kept under certain row counts and file sizes.\n- **Scan Limits:** Calculates usage percentages for every document in the organization.\n- **Linhas (%):** Based on the standard 5,000 row "soft limit" for optimal performance.\n- **Dados (%):** Based on a 10MB SQLite file size limit. Helps you identify docs that need optimization or history clearing.',
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
    """Adds multiple records to a table."""
    base_url = base_url.strip().rstrip("/")
    try:
        url = f"{base_url}/docs/{doc_id}/tables/{table_id}/records"
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
            return True, "Tabela criada."
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
    try:
        rules_records = fetch_table_records(base_url, api_key, doc_id, '_grist_ACLRules')
        resources_records = fetch_table_records(base_url, api_key, doc_id, '_grist_ACLResources')
    except Exception as e:
        st.error(i18n[st.session_state.lang]["err_fetch_rules"].format(e=e))
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
    current = fetch_table_records(base_url, api_key, doc_id, '_grist_ACLRules')
    if current:
        ids_to_del = [r['id'] for r in current]
        url_del = f"{base_url}/docs/{doc_id}/tables/_grist_ACLRules/data/delete"
        requests.post(url_del, headers=get_auth_headers(api_key), json=ids_to_del)
    all_res = fetch_table_records(base_url, api_key, doc_id, '_grist_ACLResources')
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
    # ... rest of access code ...
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
            disp_cols = [c for c in ['Email', 'Nome', 'Acesso Global'] if c in df_display.columns]
            df_display = df_display[disp_cols]
            if f_name: df_display = df_display[df_display['Nome'].str.contains(f_name, case=False, na=False)]
            if f_email: df_display = df_display[df_display['Email'].str.contains(f_email, case=False, na=False)]
            st.dataframe(df_display, use_container_width=True, hide_index=True)
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
                    for e in list_e: update_doc_access(CURRENT_BASE_URL, AUTH_API_KEY, tid, e, rl)
                    st.toast(i18n[st.session_state.lang]['toast_added']); st.cache_data.clear(); time.sleep(1); st.rerun()
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
                ed_json = st.text_area(i18n[st.session_state.lang]["new_json_rules"])
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
    tab7, tab_trans, tab6, tab8, tab10 = st.tabs([
        i18n[st.session_state.lang]['tab_cloner'],
        i18n[st.session_state.lang]['tab_transporter'],
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
                            recs = fetch_table_records(CURRENT_BASE_URL, AUTH_API_KEY, did, sel_t)
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
        js_raw = st.text_area(i18n[st.session_state.lang]["blueprint_json"])
        
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
                    tpl.append({"table_id": tid, "records": [{c['id']: "..." for c in cols if not c['fields'].get('isFormula')}]})
                st.session_state.ia_tpl = json.dumps(tpl, indent=2)
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
