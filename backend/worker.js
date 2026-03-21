export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const targetUrl = url.searchParams.get("url"); // The Google Video URL

    if (!targetUrl) {
      return new Response("Missing 'url' parameter", { 
        status: 400,
        headers: { "Access-Control-Allow-Origin": "*" }
      });
    }

    // Support CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, OPTIONS",
          "Access-Control-Allow-Headers": "Range",
          "Access-Control-Max-Age": "86400",
        },
      });
    }

    // Set up headers to mimic a real browser
    const headers = new Headers();
    headers.set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36");
    headers.set("Referer", "https://www.youtube.com/");
    
    // Forward the Range header for seeking/scrubbing support
    const range = request.headers.get("Range");
    if (range) {
      headers.set("Range", range);
    }

    try {
      const response = await fetch(targetUrl, {
        method: "GET",
        headers: headers,
        redirect: "follow"
      });

      // Create a new response to pipe the stream back with CORS enabled
      const newResponse = new Response(response.body, response);
      newResponse.headers.set("Access-Control-Allow-Origin", "*");
      newResponse.headers.set("Access-Control-Expose-Headers", "Content-Length, Content-Range, Accept-Ranges");
      
      return newResponse;
    } catch (e) {
      return new Response(`Error: ${e.message}`, { 
        status: 500,
        headers: { "Access-Control-Allow-Origin": "*" }
      });
    }
  },
};
