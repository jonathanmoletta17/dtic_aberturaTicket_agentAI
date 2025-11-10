# Importação e exportação de tópicos e agentes

Guia de ALM para mover conteúdo entre agentes e ambientes, incluindo tópicos em YAML.

## Conceitos
- Soluções (unmanaged) são o “contêiner” para exportar e importar agentes e componentes.
- É possível compartilhar e reutilizar componentes (tópicos, conhecimento, ações, entidades) entre agentes via “Component collections” (preview).
- A Microsoft planeja e disponibiliza capacidades de import/export em nível de tópico para reutilização entre ambientes/copilots.

Fontes:
- Export and import agents using solutions – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-import-export
- Create reusable component collections (preview) – Microsoft Learn: https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-export-import-copilot-components
- Release plan (import/export de tópicos) – Microsoft Learn: https://learn.microsoft.com/en-us/power-platform/release-plan/2024wave2/microsoft-copilot-studio/import-export-topics-across-copilots-environments

## Passo a passo – Exportar agente via solução
1. Crie uma solução personalizada e adicione seu agente.
2. Adicione objetos requeridos (tópicos, fluxos) usando “Add required objects”.
3. Exporte a solução (unmanaged) e transfira para o outro ambiente.
4. Importe a solução no ambiente de destino.
5. Reconfigure autenticação quando necessário e publique o agente.

Detalhes e limitações:
- Comentários em nível de tópico/nó não são exportados.
- Não remova/edite componentes diretamente pela solução; faça alterações pela UI de autoria do Copilot Studio.
- Soluções gerenciadas não podem ser exportadas; crie uma nova solução unmanaged quando necessário.
- Import pode falhar se faltarem componentes; baixe o log XML para diagnosticar.
- Não é possível exportar soluções com agentes que tenham nomes de tópicos contendo ponto (`.`).

Fonte: Export and import agents using solutions – Microsoft Learn.

## Component collections (preview)
- Coleções reúnem tópicos, conhecimento, ações, entidades e podem ser compartilhadas entre múltiplos agentes.
- Edite/adicione componentes apenas por autores com permissões (system customizer/admin).
- Exporte/importa coleções por soluções; lembre de incluir componentes novos na solução.

Fonte: Create reusable component collections (preview) – Microsoft Learn.

## Import/Export em nível de tópico
- Capacidade voltada para reutilização, escalabilidade e centros de excelência.
- Ajuda a particionar trabalho e acelerar a criação entre múltiplos bots.

Fonte: Release plan 2024 Wave 2 – Microsoft Learn.

## Boas práticas de ALM
- Padronize `Publisher` e versionamento nas soluções.
- Evite pontos nos nomes de tópicos; crie convenções claras.
- Publique o agente após a importação e valide tópicos críticos no painel de teste.