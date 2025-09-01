# mtcli-trade
  
Este é um plugin para mtcli que adiciona o comando trade para gerenciamento de ordens e posições.
  
---
  
## Instalação
  
```cmd
pip install mtcli-trade
```
  
---
  
## Comandos
  
- compra a mercado: `mt trade buy --symbol WINV25` (compra a mercado o ativo WINV25).  
- compra limitada: `mt trade buy --symbol WINV25 --limit --preco 140200` (compra limitada do WINV25 no preço 140200).  
- venda a mercado: `mt trade sell --symbol WINV25` (vende a mercado o ativo WINV25).  
- venda limitada: `mt trade sell --symbol WINV25 --limit --preco 140800` (venda limitada do WINV25 no preço 140800).  
- exibe todas as ordens pendentes:  
`mt trade orders` (exibe todas as ordens pendentes),  
`mt trade orders --symbol WINV25`(exibe todas as ordens pendentes de WINV25).  
- Cancela todas as ordens pendentes:  
`mt trade cancel` (cancela todas as ordens pendentes),  
`mt trade cancel --symbol WINV25`(cancela todas as ordens pendentes de WINV25).  
- exibe todas as posições abertas:  
`mt trade pos` (exibe todas as posições abertas),    
`mt trade pos --symbol WINV25`(exibe todas as posições abertas de WINV25).  
- Encerra todas as posições abertas:  
`mt trade zera` (encerra todas as posições abertas),    
`mt trade zera --symbol WINV25`(encerra todas as posições abertas de WINV25).  
