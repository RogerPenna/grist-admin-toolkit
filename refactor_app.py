
import re

file_path = r'C:\gristpqctest\grist_admin_toolkit.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix typo sub_d2 -> tab_trans
content = content.replace('with sub_d2:', 'with tab_trans:')

# 2. Extract modules
# Gestão de Acessos: from L585 to L1279
# Engenharia de Dados: from L1280 to L2197
# Sistema: from L2198 to end

# Actually, Tab 10 is currently at the end of the file.
# Let's find each tab block by its comment and 'with tabX:'

def get_block(tab_name):
    # Find start of block
    # Search for "with tabX:" at 4 spaces indentation
    pattern = rf'^\s{{4}}with {tab_name}:'
    match = re.search(pattern, content, re.MULTILINE)
    if not match:
        return None
    start = match.start()
    
    # Find end of block (next "with tabX:" at 4 spaces OR next module "elif main_menu" OR end of file)
    next_tab = re.search(r'^\s{4}with tab\w+:', content[match.end():], re.MULTILINE)
    next_module = re.search(r'^elif main_menu ==', content[match.end():], re.MULTILINE)
    
    ends = []
    if next_tab: ends.append(match.end() + next_tab.start())
    if next_module: ends.append(match.end() + next_module.start())
    
    if not ends:
        end = len(content)
    else:
        end = min(ends)
    
    return content[start:end]

# Extract tabs
tab6_code = get_block('tab6')
tab_trans_code = get_block('tab_trans')
tab7_code = get_block('tab7')
tab8_code = get_block('tab8')
tab10_code = get_block('tab10')
tab9_code = get_block('tab9')

# Build new Engenharia de Dados block
new_eng_dados = 'elif main_menu == "🏗️ Engenharia de Dados":\n'
new_eng_dados += '    tab7, tab_trans, tab6, tab8, tab10 = st.tabs(["🏗️ Clonador", "🚚 Transportador", "⚖️ Auditoria Integridade", "🛠️ Blueprint", "📥 IA"])\n\n'
new_eng_dados += tab7_code.strip() + '\n\n'
new_eng_dados += tab_trans_code.strip() + '\n\n'
new_eng_dados += tab6_code.strip() + '\n\n'
new_eng_dados += tab8_code.strip() + '\n\n'
new_eng_dados += tab10_code.strip() + '\n\n'

# Build new Sistema block
new_sistema = 'elif main_menu == "⚙️ Sistema":\n'
new_sistema += '    tab9, tab_help = st.tabs(["📊 Limites", "❓ Ajuda"])\n\n'
new_sistema += tab9_code.strip() + '\n\n'
new_sistema += '    with tab_help:\n'
new_sistema += '        st.header("❓ Manual de Ajuda")\n'
new_sistema += '        st.markdown("""\n'
new_sistema += '        ### 🔐 Gestão de Acessos\n'
new_sistema += '        - **Visão Global:** Visualize todos os usuários da organização.\n'
new_sistema += '        - **Mapeamento:** Mapeie quais usuários têm acesso a quais documentos.\n'
new_sistema += '        - **Ações Rápidas:** Adicione ou remova usuários em massa de documentos.\n'
new_sistema += '        - **Regras (ACL):** Visualize e edite as regras de acesso de um documento.\n\n'
new_sistema += '        ### 🏗️ Engenharia de Dados\n'
new_sistema += '        - **Clonador:** Copie a estrutura de uma tabela para outros documentos.\n'
new_sistema += '        - **Transportador:** Copie estrutura e dados de tabelas entre documentos.\n'
new_sistema += '        - **Auditoria Integridade:** Verifique se os acessos reais coincidem com os registros de uma tabela.\n'
new_sistema += '        - **Blueprint:** Crie documentos e estruturas via JSON.\n'
new_sistema += '        - **IA:** Gere templates para popular tabelas usando IA.\n\n'
new_sistema += '        ### ⚙️ Sistema\n'
new_sistema += '        - **Limites:** Monitore o uso de linhas e dados dos seus documentos.\n'
new_sistema += '        """)\n\n'

# Replace the entire section from L1280 to the end
# Find the start of the section
start_pattern = r'^elif main_menu == "ðŸ—ï¸ Engenharia de Dados":'
match_start = re.search(start_pattern, content, re.MULTILINE)
if match_start:
    content = content[:match_start.start()] + new_eng_dados + new_sistema

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Refactor complete!")
