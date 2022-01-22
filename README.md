# PetCalendar


## Bootstrapについて

- colorを変更したかったので、パッケージをダウンロードして再作成している
  ```
  git clone https://github.com/twbs/bootstrap.git
  npm i
  npm run dist
  ```
  でdistフォルダにできる  
  bootstrap.min.css  
  bootstrap.bundle.min.js  
  をそれぞれ  
  bootstrap.min.custom.css  
  bootstrap.bundle.custom.min.js  
  として使っている.  

- 変更したのは、scss/_variables.scssで、  
  primary colorを viridian(#00885a)に、  
  そのままだと文字色が黒だったので、  
  $min-contrast-ratio を4.5から3に変えた  

- バージョンは現時点最新の5.1.3を使用
