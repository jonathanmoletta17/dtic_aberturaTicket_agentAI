# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [2.0.0] - 2024-12-19

### ✨ Adicionado
- **Validação de Expressões PowerFx**: Sistema detecta e rejeita expressões PowerFx não processadas
- **Health Check Endpoint**: `/api/health` para monitoramento do sistema
- **Logging Estruturado**: Logs detalhados com trace IDs para debugging
- **Documentação Melhorada**: Docstrings e comentários mais claros
- **Tratamento de Erros Robusto**: Respostas de erro mais informativas

### 🔧 Melhorado
- **Validação de Dados**: Verificações mais rigorosas nos dados de entrada
- **Estrutura do Código**: Organização e limpeza do código fonte
- **Configuração UTF-8**: Suporte completo para caracteres especiais
- **Mapeamento de Categorias**: Interface mais amigável para categorias GLPI

### 🐛 Corrigido
- **Erro 500**: Correção do erro "'str' object has no attribute 'get'"
- **Expressões PowerFx**: Tratamento adequado de placeholders não processados
- **Encoding**: Problemas de codificação de caracteres especiais

### 🗑️ Removido
- Arquivos de teste temporários
- Código redundante e comentários desnecessários

## [1.0.0] - 2024-12-18

### ✨ Inicial
- Implementação básica da API Flask
- Integração com GLPI
- Configuração do Copilot Studio
- Criação de tickets básica