dropbox apiのテスト
=====================

以下のブログ記事で作るサンプルのソースになります。

http://lowlevellife.com/2011/11/概要-pythonで始めるdropboxapi/


dotcloudにデプロイする場合
--------------------
dotcloud用に作ってありますので、
dotcloudにデプロイして、
環境変数を設定してください。

::

  $ dotcloud var set yourappname \
      'SECRET_KEY=YOUR_SECRET_KEY' \
      'APP_KEY=YOUR_APP_KEY' \
      'APP_SECRET=YOUR_APP_SECRET'

各値は以下に変更してください。

YOUR_SECRET_KEY
  ランダムな文字列に変更

YOUR_APP_KEY
  Dropboxで登録したアプリのAPP KEYに変更

YOUR_APP_SECRET
  Dropboxで登録したアプリのAPP SECRETに変更

