# Fonte dos materiais de estudo

O banco contém 120 questões autorais baseadas no simulador deste repositório. Os arquivos finais ficam em `docs/QUESTOES_ESTUDO.md` e `docs/QUESTOES_ESTUDO.docx`.

Para editar as questões, altere `banco_questoes.py`. Cada registro contém enunciado, resposta correta pelo texto, quatro distratores, comentário, referência ao código e, quando aplicável, trecho Python e sugestão de treino.

Para regenerar os dois formatos a partir da pasta raiz:

```powershell
python -B materiais/gerar_questoes.py
```

O gerador usa somente a biblioteca padrão Python. Ele distribui as respostas entre A–E de modo determinístico, com 24 respostas por letra, e mantém os dois gabaritos sincronizados. Verifica numeração, quantidade de alternativas, respostas, correspondência de textos e integridade ZIP/XML do DOCX.

Este é um utilitário de documentação que grava somente os dois materiais solicitados. Ele é independente do simulador, que continua com dados virtuais e registros em memória. As modificações sugeridas nas questões não foram aplicadas ao código da aplicação.
