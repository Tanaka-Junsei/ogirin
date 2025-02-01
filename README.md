# ogirin

## リンク

- [大喜林](https://ogirin.vercel.app/)

## これは何

- 大喜利のお題を生成AIを使って、作成してくれるサービス「大喜林」


## 構成図

```mermaid
flowchart TB
  node_1["Cloud Run"]
  node_2["Supabase Edge Functions"]
  node_3["Supabase Database"]
  node_4["Vercel"]
  node_4 --"補充リクエストを送信"--> node_2
  node_2 --"生成リクエストを送信"--> node_1
  node_1 --"お題を生成"--> node_2
  node_2 --"DBにお題を登録"--> node_3
  node_4 --"お題を取得"--> node_2
```

## 詳細

### Cloud Run
- FastAPIで実装
- LLMによるお題生成を実行

### Supabase Edge Functions
- Vercelからリクエストを受け取り、Cloud Runにお題生成リクエストを送信
- Cloud RunからのレスポンスをSupabase Databaseに登録
- お題の各種前処理を行う

### Supabase Database
- PostgreSQL Databaseでお題を管理
- 認証機能は随時実装予定

### Vercel
- Next.jsで実装
- お題の残り件数が足りなくなった時点でEdge Functionsを呼び出し
