# Plano de Teste e Análise Aprofundada: Autenticação de Usuário Final (GLPI + Copilot Studio)

Este documento consolida cenários, riscos e recomendações para autenticação de usuários finais no GLPI via Copilot Studio, garantindo rastreabilidade (autor real) sem usar tokens pessoais compartilhados do operador.

## Problema Central

- O uso de `APP_TOKEN` e `USER_TOKEN` estáticos do desenvolvedor registra todos os tickets como se fossem criados pelo operador, quebrando a auditoria e métricas.
- Objetivo: o bot deve criar tickets “em nome” do usuário final (ex.: Maria), com autoria e histórico aparecendo como o próprio usuário no GLPI.

## Cenários de Autenticação

### 1) Login/Senha (Não recomendado)
- Viabilidade técnica: alta (endpoint `/initSession` aceita `login/password` e retorna `session_token`).
- Riscos: UX e confiança do usuário; compliance (LGPD/GDPR); exposição de credenciais do AD; dependência de mascaramento.
- Veredito: descartar para uso em produção. Manter apenas para testes/controlado em sandbox.

### 2) Token Pessoal por Usuário (Recomendado)
- Viabilidade: alta; requer “onboarding” de primeira utilização.
- Segurança: boa; token revogável, escopo apenas API.
- Fluxo (Copilot Studio + Dataverse):
  - Onboarding: quando não há token no Dataverse para `System.User.Id`, orientar usuário a gerar token pessoal no GLPI, coletar, mascarar e armazenar com segurança (criptografado ou via Key Vault).
  - Dia a dia: recuperar token do Dataverse, iniciar sessão: `Authorization: user_token <token>`, criar ticket, encerrar sessão.
- Resultado: auditoria e autoria corretas como usuário final.

### 3) SSO (OIDC/Azure AD/CAS) – Enterprise
- UX superior, porém complexidade maior; usualmente via UI.
- GLPI suporta `phpCAS` e “variáveis SSO externas” (`ssovariables_id`, `ssologout_url`) para sessão web.
- A API REST não expõe login SSO; para automação, adota-se:
  - Reverse proxy com OIDC injetando cabeçalhos/cookies reconhecidos pelo GLPI na UI (não na REST);
  - Serviço intermediário que autentica usuário no GLPI via UI e realiza ações em nome dele (mais complexo).
- Veredito: possível em ambientes corporativos com identidade integrada, mas fora do escopo direto da REST; mantenha “token pessoal” como solução pragmática imediata.

## Testes Implementados (Sandbox)

- Script `scripts/test_auth_glpi.py`: cenários `user_token` e `password`, criação de ticket, verificação de autoria e `killSession`.
- Fallbacks na criação de ticket para compatibilizar diferentes versões (`input` wrapper e campos mínimos).
- Logs por cenário em `scripts/logs/`, sem segredos.

### Resultados:
- `user_token`: autoria alinhada ao usuário do token; em nossa instância, campos relevantes: `users_id_recipient` e `users_id_lastupdater`.
- `password`: funcional em sandbox; auditoria como o próprio usuário; não recomendado para produção.
- Logout: algumas instâncias mantêm token válido até o TTL; o teste reporta `logout_verified=false` quando o token não é invalidado imediatamente.

## Mapeamento de Identidade (M365 → GLPI)

- Script `scripts/test_identity_mapping.py`: abre sessão via `user_token` ou `password`, busca usuário em GLPI com base em UPN/login/email e retorna candidatos (id, name, email).
- Utilidade: vincular conta MS 365 (UPN) a um `users_id` do GLPI para armazenar o token pessoal correto no Dataverse.

## Integração Copilot Studio (Fluxos)

### Onboarding
- Ação: verificar no Dataverse se existe token GLPI para `System.User.Id`.
- Se não existir:
  - Orientar geração de token pessoal no GLPI.
  - Coletar token (variável mascarada) e armazenar com segurança.

### Abrir Chamado (Dia a Dia)
- Recuperar token do Dataverse.
- Chamar `initSession` com `App-Token` + `Authorization: user_token <token>`.
- Criar ticket com dados coletados.
- Encerrar sessão com `killSession`.

## Segurança e Compliance

- Não pedir nem armazenar senhas do AD/GLPI.
- Tokens pessoais são revogáveis e estritamente de API.
- Mascarar variáveis sensíveis no Copilot Studio; no armazenamento, criptografar ou usar Key Vault.
- Logs: mínimos e sem segredos.

## Próximos Passos

1. Adotar “Token pessoal por usuário” como padrão.
2. Criar tabela Dataverse (ex.: `UserGLPIToken`), com `UserID_AAD` e `GLPI_Token` (criptografado/cofre).
3. Implementar tópico “Onboarding” e “Abrir Chamado” conforme fluxos.
4. Opcional Enterprise: planejar SSO via OIDC/CAS para UI do GLPI.