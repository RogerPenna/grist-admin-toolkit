import re

replacements = {
    # General messages & Errors
    'st.error(f"Erro ao buscar organizações: {e}")': 'st.error(i18n[st.session_state.lang]["err_fetch_orgs"].format(e=e))',
    'st.error(f"Erro ao buscar usuários da organização: {e}")': 'st.error(i18n[st.session_state.lang]["err_fetch_org_users"].format(e=e))',
    'st.error(f"Erro ao buscar workspaces: {e}")': 'st.error(i18n[st.session_state.lang]["err_fetch_workspaces"].format(e=e))',
    'st.error(f"Erro ao buscar tabelas: {e}")': 'st.error(i18n[st.session_state.lang]["err_fetch_tables"].format(e=e))',
    'st.error(f"Erro ao buscar regras: {e}")': 'st.error(i18n[st.session_state.lang]["err_fetch_rules"].format(e=e))',
    'st.warning("Nenhuma org.")': 'st.warning(i18n[st.session_state.lang]["warn_no_org"])',
    'st.warning("Chave necessária.")': 'st.warning(i18n[st.session_state.lang]["warn_key_needed"])',
    'st.success("OK!")': 'st.success(i18n[st.session_state.lang]["msg_ok"])',
    'st.error(f"Erro: {e}")': 'st.error(i18n[st.session_state.lang]["err_generic"].format(e=e))',

    # Cloner
    'st.button("🚀 Clonar")': 'st.button(i18n[st.session_state.lang]["btn_clone"])',
    'st.success("Concluído!")': 'st.success(i18n[st.session_state.lang]["toast_completed"])',

    # Transporter
    'st.header("🚚 Transportador de Dados")': 'st.header(i18n[st.session_state.lang]["header_transporter"])',
    'st.selectbox("Doc Destino"': 'st.selectbox(i18n[st.session_state.lang]["t_dest_doc"]',
    'st.markdown("### 📝 Console de Operações")': 'st.markdown(i18n[st.session_state.lang]["console_operations"])',

    # Debug Inspector
    'st.expander("🔍 Inspetor de Dados (Debug)"': 'st.expander(i18n[st.session_state.lang]["inspector_debug"]',
    'st.markdown("Visualize os dados brutos de qualquer tabela (incluindo colunas escondidas) e exporte para análise.")': 'st.markdown(i18n[st.session_state.lang]["inspector_desc"])',
    'st.error(f"Erro ao ler esquema oculto: {e}")': 'st.error(i18n[st.session_state.lang]["err_read_hidden_schema"].format(e=e))',
    'st.error(f"Erro nos registros: {err_i}")': 'st.error(i18n[st.session_state.lang]["err_records"].format(err_i=err_i))',
    'st.subheader("📋 Metadados das Colunas (Schema)")': 'st.subheader(i18n[st.session_state.lang]["col_metadata"])',
    'st.markdown("**JSON do Schema (Debug):**")': 'st.markdown(i18n[st.session_state.lang]["json_schema"])',
    'st.subheader("📄 Registros Brutos")': 'st.subheader(i18n[st.session_state.lang]["raw_records"])',
    'st.info(f"👉 **{len(sel_insp)} linhas selecionadas.**")': 'st.info(i18n[st.session_state.lang]["x_rows_selected"].format(count=len(sel_insp)))',
    'st.markdown("**JSON dos Dados (Debug):**")': 'st.markdown(i18n[st.session_state.lang]["json_data"])',

    # Audit
    'st.header("⚖️ Auditoria de Integridade")': 'st.header(i18n[st.session_state.lang]["header_audit"])',
    'st.selectbox("Carregar Config"': 'st.selectbox(i18n[st.session_state.lang]["load_config"]',
    '["(Nova)"]': '[i18n[st.session_state.lang]["new_config"]]',
    'st.selectbox("Doc Alvo"': 'st.selectbox(i18n[st.session_state.lang]["target_doc"]',
    'st.selectbox("Tabela Ref"': 'st.selectbox(i18n[st.session_state.lang]["ref_table"]',
    'st.button("🔎 Auditoria")': 'st.button(i18n[st.session_state.lang]["btn_audit"])',
    'st.button("✨ Conceder")': 'st.button(i18n[st.session_state.lang]["btn_grant"])',
    'st.button("🗑️ Remover")': 'st.button(i18n[st.session_state.lang]["btn_remove"])',

    # Blueprint
    'st.header("🛠️ Blueprint (JSON)")': 'st.header(i18n[st.session_state.lang]["header_blueprint"])',
    'st.subheader("1. Novo Doc")': 'st.subheader(i18n[st.session_state.lang]["new_doc_section"])',
    'st.button("🆕 Criar")': 'st.button(i18n[st.session_state.lang]["btn_create"])',
    'st.success(f"Criado! {res}")': 'st.success(i18n[st.session_state.lang]["success_created"].format(res=res))',
    'st.subheader("2. Aplicar Estrutura")': 'st.subheader(i18n[st.session_state.lang]["apply_structure_section"])',
    'st.checkbox("🔥 Sobrescrita (Apagará todas as tabelas atuais)")': 'st.checkbox(i18n[st.session_state.lang]["overwrite_warning"])',
    'st.text_area("Blueprint JSON")': 'st.text_area(i18n[st.session_state.lang]["blueprint_json"])',
    'st.warning(f"⚠️ **Atenção:** Você está prestes a modificar o documento **{target_b}** no servidor **{CURRENT_BASE_URL}**.")': 'st.warning(i18n[st.session_state.lang]["warning_mod_doc"].format(target_b=target_b, CURRENT_BASE_URL=CURRENT_BASE_URL))',
    'st.checkbox("Eu confirmo que o documento alvo e o servidor estão corretos.")': 'st.checkbox(i18n[st.session_state.lang]["confirm_exec_checkbox"])',
    'st.button("🚀 Executar"': 'st.button(i18n[st.session_state.lang]["btn_exec"]',
    'st.error("JSON vazio. Marque \'Sobrescrita\' se deseja apenas limpar o documento.")': 'st.error(i18n[st.session_state.lang]["err_empty_json_overwrite"])',
    'st.info("Desativando fórmulas para evitar erros de dependência no servidor...")': 'st.info(i18n[st.session_state.lang]["info_disable_formulas"])',
    'st.error(f"Erro ao limpar documento: {m_del}")': 'st.error(i18n[st.session_state.lang]["err_clean_doc"].format(m_del=m_del))',
    'st.success(f"🧹 Limpeza concluída: {len(tables_to_delete)} tabelas removidas.")': 'st.success(i18n[st.session_state.lang]["success_clean_doc"].format(count=len(tables_to_delete)))',
    'st.info("🧹 Nenhuma tabela de usuário encontrada para limpar.")': 'st.info(i18n[st.session_state.lang]["info_no_user_tables_clean"])',
    'st.success("Operação concluída (Apenas limpeza).")': 'st.success(i18n[st.session_state.lang]["success_clean_only"])',
    'st.success("Blueprint OK!")': 'st.success(i18n[st.session_state.lang]["success_blueprint"])',

    # AI
    'st.header("📥 Popular com IA")': 'st.header(i18n[st.session_state.lang]["header_ai"])',
    'st.button("🪄 Gerar Template")': 'st.button(i18n[st.session_state.lang]["btn_gen_template"])',
    'st.multiselect("Tabelas"': 'st.multiselect(i18n[st.session_state.lang]["lbl_tables"]',
    'st.text_area("Template IA"': 'st.text_area(i18n[st.session_state.lang]["lbl_ai_template"]',
    'st.text_area("Cole Resposta IA"': 'st.text_area(i18n[st.session_state.lang]["lbl_paste_ai"]',
    'st.button("🚀 Povoar")': 'st.button(i18n[st.session_state.lang]["btn_populate"])',

    # System
    'st.button("🔍 Escanear Limites")': 'st.button(i18n[st.session_state.lang]["btn_scan_limits"])',
    'st.header("📘 Ajuda")': 'st.header(i18n[st.session_state.lang]["header_help"])',
    'st.markdown("""\n        ### 🔐 Gestão de Acessos\n        - **Visão Global:** Usuários do Team Site.\n        - **Mapeamento:** Auditoria em massa de quem acessa o quê.\n        - **Ações Rápidas:** Convites e revogações expressas.\n        \n        ### 🏗️ Engenharia de Dados\n        - **Clonador:** Copia esqueletos de tabelas.\n        - **Transportador:** Move dados entre documentos.\n        - **Auditoria:** Cruza dados de tabelas com acessos reais.\n        - **Blueprint:** Infraestrutura como código (JSON).\n        """)': 'st.markdown(i18n[st.session_state.lang]["help_markdown"])'
}

with open("grist_admin_toolkit.py", "r", encoding="utf-8") as f:
    content = f.read()

for k, v in replacements.items():
    content = content.replace(k, v)

with open("grist_admin_toolkit.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Replacements applied!")
