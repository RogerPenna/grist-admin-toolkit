# Diagnóstico: Problema de Exibição em Colunas de Referência

## Status Atual
O Transportador de Dados agora utiliza uma **Estratégia Atômica de 3 Fases**:
1. **Fase 1:** Cria colunas como `Text` (plano) para evitar validações do Sandbox.
2. **Fase 2:** Insere dados brutos (IDs numéricos e strings).
3. **Fase 3:** Atualiza as colunas (`PATCH`) para os tipos originais (`Ref`, `Choice`, `Formula`), realizando o mapeamento de IDs de exibição (`visibleCol` e `displayCol`).

## O Problema Persistente
Apesar de os dados estarem no destino e as colunas estarem configuradas como `Ref:Tabela`, o Grist continua exibindo o **ID da linha** (número) com um aviso de erro, em vez do valor da coluna de rótulo (ex: "Elemento"). 
Ao clicar duas vezes na célula, o Grist reconhece a referência correta, o que indica que:
- O tipo da coluna está correto.
- O dado (ID) inserido é válido.
- O mapeamento de `visibleCol` via API `PATCH` não está sendo "assimilado" pelo motor visual do Grist como esperado.

## Próximos Passos
1. **Investigar o "Grist Table Lens":** Analisar como o outro projeto modular lida com a resolução de referências e se utiliza algum endpoint específico para "forçar" a atualização da visualização ou se há campos de metadados adicionais (como `displayCol` em nível de widget).
2. **Refinar Mapeamento:** Verificar se o Grist exige que o `visibleCol` seja definido no momento da criação da tabela (Fase 1) mesmo que o tipo seja Texto, ou se há uma dependência de ordem entre `displayCol` e `visibleCol`.
3. **Análise de Widgets:** Verificar se a estrutura de páginas/widgets influencia na forma como a API de colunas interpreta o rótulo de exibição.

---
*Documentado em 01/06/2026 - Gemini CLI*
