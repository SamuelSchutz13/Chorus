import 'reflect-metadata';
import { Module } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { NestExpressApplication } from '@nestjs/platform-express';
import { join } from 'node:path';
import { MusicaController } from './musica.controller';
import { MusicaService } from './musica.service';

@Module({ controllers: [MusicaController], providers: [MusicaService] })
class AppModule {}

async function bootstrap() {
  const app = await NestFactory.create<NestExpressApplication>(AppModule);
  app.useStaticAssets(join(__dirname, '..', 'public'));
  const port = process.env.PORT ?? 3000;
  await app.listen(port);
  console.log(`Abra http://localhost:${port}`);
}
bootstrap();
