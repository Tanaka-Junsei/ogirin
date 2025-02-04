import { serve } from "https://deno.land/std@0.192.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// 環境変数の取得
const PROJECT_URL = Deno.env.get("PROJECT_URL")!;
const ANON_KEY = Deno.env.get("ANON_KEY")!;
const ODAI_API_URL = Deno.env.get("ODAI_API_URL")!; // お題生成APIのエンドポイント

// Supabaseクライアントを作成
const supabase = createClient(PROJECT_URL, ANON_KEY);

// CORSヘッダー設定
const headers = new Headers({
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
  "Content-Type": "application/json",
});

// Deno Edge Function のエントリーポイント
serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers });
  }

  try {
    console.log("Received request");

    // リクエストヘッダーから生成件数を取得（デフォルト: 1）
    const { number } = await req.json().catch(() => ({ number: 1 }));

    if (!number || typeof number !== "number" || number <= 0) {
      return new Response(JSON.stringify({ error: "Invalid 'number' value" }), {
        status: 400,
        headers,
      });
    }

    console.log(`Requesting ${number} odai(s) from ODAI_API_URL: ${ODAI_API_URL}`);

    // お題生成APIを呼び出す
    const odaiResponse = await fetch(ODAI_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ number }),
    });

    if (!odaiResponse.ok) {
      const errorText = await odaiResponse.text();
      console.error("Failed to fetch odai:", errorText);
      return new Response(
        JSON.stringify({ error: "Failed to fetch odai", details: errorText }),
        { status: 500, headers }
      );
    }

    const odaiData = await odaiResponse.json();
    console.log("Received odaiData:", odaiData);

    if (!odaiData.response || !Array.isArray(odaiData.response) || odaiData.response.length === 0) {
      console.error("Invalid odai response format:", odaiData);
      return new Response(JSON.stringify({ error: "Invalid odai response format" }), {
        status: 500,
        headers,
      });
    }

    // SupabaseのDBにお題を一括挿入 
    const insertData = odaiData.response.map((odaiText) => ({ text: odaiText }));
    console.log("Inserting into Supabase:", insertData);

    const { error } = await supabase.from("odai").insert(insertData);

    if (error) {
      console.error("Error inserting odai:", error);
      return new Response(JSON.stringify({ error: "Error saving odai to database" }), {
        status: 500,
        headers,
      });
    }

    return new Response(
      JSON.stringify({ message: "Odai saved successfully", odai: insertData }),
      { status: 200, headers }
    );
  } catch (error) {
    console.error("Error processing request:", error);
    return new Response(JSON.stringify({ error: "Error processing request" }), {
      status: 500,
      headers,
    });
  }
});

/* To invoke locally:

  1. Run `supabase start` (see: https://supabase.com/docs/reference/cli/supabase-start)
  2. Make an HTTP request:

  curl -i --location --request POST 'http://127.0.0.1:54321/functions/v1/reload-odai' \
    --header 'Authorization: Bearer YOUR_SUPABASE_ANON_KEY' \
    --header 'Content-Type: application/json' \
    --data '{"number": 3}'

*/
