# OdfEdit CLI (Português)

Esta é uma ferramenta de linha de comando para converter arquivos de definição de órgão do Hauptwerk para o formato GrandOrgue.

## Instalação

Para instalar a ferramenta em seu sistema Linux, siga os passos abaixo:

1.  **Abra o terminal** e navegue até o diretório do projeto (`/workspaces/OdfEdit`).
2.  **Execute o seguinte comando** para instalar a biblioteca:

    ```bash
    pip install .
    ```

Após a instalação, um novo comando chamado `odf-converter` estará disponível em seu sistema.

## Como Usar

1.  Coloque os arquivos de definição do Hauptwerk que você deseja converter na pasta `entrada`.
2.  Execute o comando de conversão no terminal.

### Comando Básico

Se você colocar o arquivo `seu_orgao.xml` na pasta `entrada`, o seguinte comando irá convertê-lo e salvar o resultado em `saida/seu_orgao.organ`:

```bash
odf-converter --input_file seu_orgao.xml
```

### Especificando Arquivo de Saída

Você pode especificar um nome e local diferente para o arquivo de saída:

```bash
odf-converter --input_file seu_orgao.xml --output_file /caminho/para/outro/local/novo_nome.organ
```

### Opções Disponíveis

*   `--output_file`: Especifica o caminho para o arquivo de saída `.organ`.
*   `--convert-tremulants`: Converte samples com tremulante.
*   `--separate-tremulant-ranks`: Coloca samples com tremulante em ranks separados.
*   `--pitch-correct-metadata`: Corrige o pitch dos tubos a partir dos metadados dos samples.
*   `--pitch-correct-filename`: Corrige o pitch dos tubos a partir do nome do arquivo dos samples.
*   `--convert-alt-layouts`: Converte layouts de tela alternativos.
*   `--no-keys-noise`: Não converte os ruídos das teclas.
*   `--convert-unused-ranks`: Converte ranks do Hauptwerk não utilizados.
*   `--encoding`: Define a codificação do arquivo de saída (ex: `utf-8-sig`, `iso-8859-1`).