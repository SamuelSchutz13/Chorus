import { BadRequestException, Controller, Get, Param, ParseIntPipe, Query } from '@nestjs/common';
import { MusicaService } from './musica.service';

const texto = (valor: string | undefined, campo: string) => {
  const t = valor?.trim();
  if (!t || t.length > 200) throw new BadRequestException(`Informe ${campo} (até 200 caracteres)`);
  return t;
};

@Controller('api')
export class MusicaController {
  constructor(private readonly musica: MusicaService) {}

  @Get('search')
  search(@Query('q') q?: string) {
    return this.musica.search(texto(q, 'o nome da música'));
  }

  @Get('song/:id')
  song(@Param('id', ParseIntPipe) id: number) {
    return this.musica.song(id);
  }

  @Get('artist/:id/songs')
  artistSongs(@Param('id', ParseIntPipe) id: number) {
    return this.musica.artistSongs(id);
  }

  @Get('chords')
  chords(@Query('artist') artist?: string, @Query('title') title?: string) {
    return this.musica.chords(texto(artist, 'o artista'), texto(title, 'a música'));
  }
}
