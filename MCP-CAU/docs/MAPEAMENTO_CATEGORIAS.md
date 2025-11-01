# Mapeamento de Categorias: User-Friendly → GLPI

## 🎯 Objetivo
Mapear categorias simples e intuitivas para as categorias técnicas do GLPI, facilitando a experiência do usuário.

## 📋 Categorias User-Friendly

### 1. 🖥️ HARDWARE - Computador/Notebook
**Categoria GLPI:** `Tipos de computador`
**Subcategorias GLPI:**
- Desktop
- Laptop
- Workstation
- Thin client

**Exemplos de problemas:**
- Computador não liga
- Tela azul
- Lentidão extrema
- Problemas de hardware

---

### 2. 🖨️ HARDWARE - Impressora
**Categoria GLPI:** `Tipos de impressora`
**Subcategorias GLPI:**
- Impressora jato de tinta
- Impressora laser
- Multifuncional
- Plotter

**Exemplos de problemas:**
- Impressora não imprime
- Papel atolado
- Toner/tinta acabou
- Problemas de conexão

---

### 3. 📺 HARDWARE - Monitor/Equipamentos
**Categoria GLPI:** `Tipos de monitor`
**Subcategorias GLPI:**
- Monitor LCD
- Monitor LED
- Projetor
- Equipamentos periféricos

**Exemplos de problemas:**
- Monitor sem imagem
- Resolução incorreta
- Cabo com defeito
- Equipamentos não funcionam

---

### 4. 💻 SOFTWARE - Aplicativos/Programas
**Categoria GLPI:** `Categorias de software`
**Subcategorias GLPI:**
- Software de escritório
- Software de sistema
- Aplicativos específicos
- Licenças

**Exemplos de problemas:**
- Programa não abre
- Erro de licença
- Instalação de software
- Atualização necessária

---

### 5. 🌐 CONECTIVIDADE - Internet/Rede
**Categoria GLPI:** `Redes`
**Subcategorias GLPI:**
- Redes WiFi
- Redes cabeadas
- VPN
- Conectividade geral

**Exemplos de problemas:**
- Sem internet
- WiFi não conecta
- Rede lenta
- VPN não funciona

---

### 6. 🔐 SEGURANÇA - Acesso/Login
**Categoria GLPI:** `Categorias ITIL`
**Subcategorias GLPI:**
- Gestão de identidade
- Controle de acesso
- Segurança da informação
- Autenticação

**Exemplos de problemas:**
- Esqueci a senha
- Conta bloqueada
- Problemas de login
- Acesso negado

---

### 7. 📋 SOLICITAÇÃO - Instalação/Configuração
**Categoria GLPI:** `Assistência`
**Subcategorias GLPI:**
- Instalação de software
- Configuração de equipamentos
- Solicitações diversas
- Suporte técnico

**Exemplos de problemas:**
- Instalar programa
- Configurar email
- Solicitar equipamento
- Suporte geral

---

### 8. ❓ OUTROS - Não listado acima
**Categoria GLPI:** `Geral`
**Subcategorias GLPI:**
- Problemas diversos
- Categorias não especificadas
- Outros tipos de chamado

**Exemplos de problemas:**
- Problema não categorizado
- Dúvidas gerais
- Outros tipos de suporte

## 🔄 Implementação no Código

### Estrutura do Mapeamento
```json
{
  "HARDWARE_COMPUTADOR": {
    "display": "🖥️ HARDWARE - Computador/Notebook",
    "glpi_category": "Tipos de computador",
    "glpi_subcategory": "Desktop"
  },
  "HARDWARE_IMPRESSORA": {
    "display": "🖨️ HARDWARE - Impressora",
    "glpi_category": "Tipos de impressora", 
    "glpi_subcategory": "Impressora laser"
  },
  "HARDWARE_MONITOR": {
    "display": "📺 HARDWARE - Monitor/Equipamentos",
    "glpi_category": "Tipos de monitor",
    "glpi_subcategory": "Monitor LCD"
  },
  "SOFTWARE": {
    "display": "💻 SOFTWARE - Aplicativos/Programas",
    "glpi_category": "Categorias de software",
    "glpi_subcategory": "Software de escritório"
  },
  "CONECTIVIDADE": {
    "display": "🌐 CONECTIVIDADE - Internet/Rede",
    "glpi_category": "Redes",
    "glpi_subcategory": "Redes WiFi"
  },
  "SEGURANCA": {
    "display": "🔐 SEGURANÇA - Acesso/Login",
    "glpi_category": "Categorias ITIL",
    "glpi_subcategory": "Gestão de identidade"
  },
  "SOLICITACAO": {
    "display": "📋 SOLICITAÇÃO - Instalação/Configuração",
    "glpi_category": "Assistência",
    "glpi_subcategory": "Instalação de software"
  },
  "OUTROS": {
    "display": "❓ OUTROS - Não listado acima",
    "glpi_category": "Geral",
    "glpi_subcategory": "Problemas diversos"
  }
}
```

## 🎨 Interface no Copilot Studio

### Pergunta de Categoria
```
"Por favor, selecione a categoria que melhor descreve seu problema:

🖥️ HARDWARE - Computador/Notebook
🖨️ HARDWARE - Impressora  
📺 HARDWARE - Monitor/Equipamentos
💻 SOFTWARE - Aplicativos/Programas
🌐 CONECTIVIDADE - Internet/Rede
🔐 SEGURANÇA - Acesso/Login
📋 SOLICITAÇÃO - Instalação/Configuração
❓ OUTROS - Não listado acima"
```

### Variáveis no Copilot Studio
- `Topic.CategoryUserFriendly` - Categoria selecionada pelo usuário
- `Topic.CategoryGLPI` - Categoria mapeada para GLPI
- `Topic.SubcategoryGLPI` - Subcategoria mapeada para GLPI

## 📊 Benefícios

### Para o Usuário
- ✅ **Simples**: Apenas 8 opções claras
- ✅ **Intuitivo**: Ícones e descrições amigáveis
- ✅ **Rápido**: 1 clique para selecionar
- ✅ **Visual**: Emojis facilitam identificação

### Para o Sistema
- ✅ **Compatível**: Mapeia para categorias GLPI existentes
- ✅ **Manutenível**: Fácil ajustar mapeamentos
- ✅ **Escalável**: Pode adicionar subcategorias
- ✅ **Rastreável**: Mantém histórico de categorização

## 🚀 Próximos Passos

1. **Implementar no agente** - Adicionar seleção de categoria
2. **Testar mapeamento** - Verificar se categorias chegam corretamente no GLPI
3. **Ajustar conforme necessário** - Refinar baseado no feedback
4. **Documentar para usuários** - Criar guia de categorias