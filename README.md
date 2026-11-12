<p align="center">
  <img src="public/icon.svg" alt="" width="72" />
</p>

<h1 align="center">Chorus</h1>

<p align="center">
  Digite o nome de uma música e veja a letra, a tradução, a cifra e onde ouvir, tudo numa página só. Sem cadastro e sem anúncio.
</p>

<p align="center">
  <img alt="NestJS 11" src="https://img.shields.io/badge/NestJS-11-e0234e?logo=nestjs&logoColor=white" />
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-strict-3178c6?logo=typescript&logoColor=white" />
  <img alt="Python 3" src="https://img.shields.io/badge/Python-3-3776ab?logo=python&logoColor=white" />
  <img alt="Scrapling" src="https://img.shields.io/badge/Scrapling-0.5-2ead33" />
  <img alt="Genius" src="https://img.shields.io/badge/fonte-Genius-ffff64?logo=genius&logoColor=black" />
</p>

> [!NOTE]
> **Nada fica salvo.** O Chorus não tem banco de dados. As páginas do Genius, do Letras.mus.br e do Cifra Club são raspadas na hora com o [Scrapling](https://github.com/D4Vinci/Scrapling), e o resultado fica só num cache em memória por 24 horas.

## Funções

- **Busca enquanto digita**: os resultados aparecem meio segundo depois que você para de digitar.
- **Onde ouvir**: links para YouTube, Spotify, Apple Music, SoundCloud e Deezer, com o ícone de cada um.
- **Letra caprichada**: estrofes separadas, e marcações como `[Refrão]` e `[Verso 1]` viram títulos.
- **Traduções com bandeira**: um dropdown com todas as traduções que o Genius tiver. Ao escolher uma, a original e a tradução aparecem **lado a lado**, estrofe por estrofe.
- **Letra reserva**: quando o Genius não tem a letra, o Chorus busca no Letras.mus.br. Ajuda bastante com música brasileira.
- **Cifra**: a aba Cifra traz a cifra do Cifra Club, com os acordes destacados.
- **Diagrama dos acordes**: passe o mouse (ou toque) num acorde e veja como tocar no violão, com dedos, pestana e cordas soltas.
- **Modo leitura**: letra ou cifra em tela cheia, com A− / A+ para ajustar a fonte. O tamanho fica salvo no navegador.
- **Sobre a música**: data de lançamento, compositores, produtores e a descrição do Genius.
- **Mais do artista**: as músicas mais populares do mesmo artista, para abrir com um clique.

## Começando

Você precisa de [Node.js](https://nodejs.org) **20 ou mais novo** e [Python](https://www.python.org) **3.10 ou mais novo**.

```sh
git clone https://github.com/SamuelSchutz13/Chorus.git
cd Chorus

pip install scrapling
npm install
npm start          # http://localhost:3000
```

Abra http://localhost:3000 e digite o nome de uma música.

### Configuração

| Variável | Descrição                                                       |
| -------- | --------------------------------------------------------------- |
| `PORT`   | Porta do servidor (padrão `3000`)                               |
| `PYTHON` | Executável do Python usado pelo scraper (padrão `python`)       |

### Scripts

| Comando         | O que faz                                                   |
| --------------- | ----------------------------------------------------------- |
| `npm start`     | Compila o TypeScript e sobe o servidor na porta 3000         |
| `npm run build` | Só compila o TypeScript para `dist/`                         |
| `npm test`      | Testa a extração de letra e a normalização de títulos        |

## API

| Rota                                    | Retorna                                                          |
| --------------------------------------- | ---------------------------------------------------------------- |
| `GET /api/search?q=evidencias`          | Lista de músicas encontradas no Genius                           |
| `GET /api/song/:id`                     | Letra, links de onde ouvir, traduções e informações da música    |
| `GET /api/artist/:id/songs`             | Músicas mais populares do artista                                |
| `GET /api/chords?artist=Queen&title=…`  | Cifra do Cifra Club (acordes marcados com ``…``)     |

O scraper também roda sozinho pelo terminal:

```sh
python scraper/genius.py search "bohemian rhapsody"
python scraper/genius.py song 1063
python scraper/genius.py chords "Queen" "Bohemian Rhapsody"
```

## Limites e segurança

- **Entrada validada no servidor**: busca, artista e título têm até 200 caracteres, e os ids precisam ser números.
- **Sem injeção de comando**: o termo digitado vai como argumento para o Python via `execFile`, nunca passa por um shell.
- **Cache com limite**: até 1000 itens por 24 horas. Pedidos iguais feitos ao mesmo tempo viram uma única consulta, e erros não ficam em cache.
- **Resultado conferido**: no Letras.mus.br e no Cifra Club, só é aceito resultado com o mesmo título. O mesmo artista e a versão original (sem "part." ou "ao vivo") têm preferência.

> [!WARNING]
> O Chorus depende do HTML e de endpoints internos do Genius, Letras.mus.br e Cifra Club. Se algum desses sites mudar, a parte correspondente pode parar de funcionar até os seletores em `scraper/genius.py` serem atualizados. Letras e cifras pertencem aos seus autores; use o projeto para estudo e uso pessoal.

## Como funciona

```
navegador (HTML + JS)  ⇄  NestJS (API + cache em memória)  ⇄  Python + Scrapling
                                                                  ├─ Genius          busca, letra, traduções, links
                                                                  ├─ Letras.mus.br   letra reserva
                                                                  └─ Cifra Club      cifra
```

Ícones das plataformas: [Simple Icons](https://simpleicons.org). Bandeiras: [flagcdn](https://flagcdn.com). Diagramas de acordes: [chords-db](https://github.com/tombatossals/chords-db).
