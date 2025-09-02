<h1>DAX_UTIL</h1>

## **Biblioteca de funcionalidades**

## Conteudo

Os pacotes que compoem esta biblioteca sao:<br>
- Cipher<br>
- DateUtils<br>
- Generic<br>
- SQL<br>
- System<br>
- WebHook<br>

<h3>Descricao dos pacotes...</h3>
<h2>Cipher:</h2>

Pacote responsavel por criptografar e descriptografar conteudos, composta 
por tres classes: RSA, AES e B64.
Peculiaridades de cada uma destas classes:<br>
- <b>RSA</b>: Criptografa textos curtos
- <b>AES</b>: Criptografa textos longos (faz uso tambem da RSA)
- <b>B64</b>: Criptografia mais vulneravel

<b><u>from Utils.Cipher import RSA, AES, B64</b></u>

Apesar de criptografar qualquer tipo de valor, nao e recomendada utilizar 
para senhas ou informacoes sensiveis pois sua vulnerabilidade e grande.<br>
***Em breve sera disponibilizadas funcionalidades para este fim neste pacote

<h2>DateUtils</h2> Pacote responsavel por manipulacao de datas e horas
<h2>Generic</h2>Funcionalidades de utilizacao generica. Principal foco e facilitar e 
diminuir aqueles codigos que ocupam varias linhas suprimindo-os em apenas uma linha,
quando possivel. Ex.:<br> 
- NVL() --> Equivalente ao NVL do ORACLE. nvl(None, "a")<br>
- IIF() --> If de uma linha so IF(value_boolean, value_True, value_False)<br>
- entre outras funconalidades<br>

<h2>SQL</h2>Ainda em desenvolvimento. Com objetivo de facilitar obtencao de valores de cursores, etc.
<h2>System</h2>Obtem informacoes do sistema operacional
<h2>WebHook</h2>Funcionalidades para conversar com TEAMS e SLACK