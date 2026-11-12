import { BadGatewayException, Injectable } from '@nestjs/common';
import { execFile } from 'node:child_process';
import { join } from 'node:path';

const SCRIPT = join(__dirname, '..', 'scraper', 'genius.py');
const PYTHON = process.env.PYTHON ?? 'python';
const TTL = 24 * 60 * 60 * 1000;
const MAX_ENTRIES = 1000;

@Injectable()
export class MusicaService {
  // shortcut: cache em memória, some ao reiniciar o servidor; trocar por Redis/arquivo se precisar persistir
  private cache = new Map<string, { at: number; value: Promise<unknown> }>();

  search(q: string) {
    return this.cached('search', q.toLowerCase());
  }

  song(id: number) {
    return this.cached('song', String(id));
  }

  artistSongs(id: number) {
    return this.cached('artist', String(id));
  }

  chords(artist: string, title: string) {
    return this.cached('chords', artist, title);
  }

  // guarda a Promise (não o resultado): pedidos iguais simultâneos viram uma única chamada ao scraper
  private cached(cmd: string, ...args: string[]) {
    const key = [cmd, ...args].join('\u0000');
    const hit = this.cache.get(key);
    if (hit && Date.now() - hit.at < TTL) return hit.value;

    const value = this.run(cmd, args);
    value.catch(() => this.cache.delete(key)); // erro não fica em cache
    this.cache.delete(key);
    this.cache.set(key, { at: Date.now(), value });
    if (this.cache.size > MAX_ENTRIES) this.cache.delete(this.cache.keys().next().value!); // Map mantém ordem de inserção: remove o mais antigo
    return value;
  }

  // execFile sem shell: o termo digitado vai como argumento, sem risco de injeção
  private run(cmd: string, args: string[]): Promise<unknown> {
    return new Promise((resolve, reject) => {
      execFile(
        PYTHON,
        [SCRIPT, cmd, ...args],
        { timeout: 30_000, env: { ...process.env, PYTHONIOENCODING: 'utf-8' } },
        (err, stdout, stderr) => {
          if (err) return reject(new BadGatewayException(`Falha no scraper: ${stderr || err.message}`));
          try {
            resolve(JSON.parse(stdout));
          } catch {
            reject(new BadGatewayException('Resposta inválida do scraper'));
          }
        },
      );
    });
  }
}
