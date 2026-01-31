# dojo2 implementation notes

- CLI repo: ~/dojo-cli
- Entry script: ./dojo2
- Workspace root: ~/dojo
- System profile: ~/dojo/system/ (IDENTITY.md, ANSWER_FORMAT.md, PROJECT_CONTEXT.template.md)

When returning to this:

1. cd ~/dojo-cli
2. Run ./dojo2  (this is the CLI for the ~/dojo workspace)
3. Use DOJO_INVENTORY.md and PROJECT_INDEX.md in ~/dojo as the source of truth for projects.
4. For any active project under ~/dojo (apps, bots, protocols, experiments, tools), create a PROJECT_CONTEXT.md from:
   ~/dojo/system/PROJECT_CONTEXT.template.md
