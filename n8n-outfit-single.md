# n8n HTTP Request - Outfit Single Endpoint

## HTTP Request Node JSON

```json
{
  "nodes": [
    {
      "parameters": {
        "method": "POST",
        "url": "http://91.99.165.243/outfit-single",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "X-API-Key",
              "value": "sk_live_0ZCdL2N_zJC7SgkeVYQykjGlPvjGUld8_sp8fB1Gdr0"
            }
          ]
        },
        "sendBody": true,
        "specifyBody": "json",
        "jsonBody": "={\n  \"images\": {\n    \"hat\": \"{{ $json.products.hat.url }}\",\n    \"hoodie\": \"{{ $json.products.hoodie.url }}\",\n    \"pants\": \"{{ $json.products.pants.url }}\",\n    \"extra\": \"{{ $json.products.extra.url }}\",\n    \"meme\": \"{{ $json.products.meme.url }}\",\n    \"shoes\": \"{{ $json.products.shoes.url }}\"\n  },\n  \"main_title\": \"{{ $json.main_title }}\",\n  \"subtitle\": \"{{ $json.subtitle }}\",\n  \"title_font_size\": 64,\n  \"subtitle_font_size\": 38,\n  \"response_format\": \"url\"\n}",
        "options": {
          "response": {
            "response": {
              "fullResponse": true
            }
          }
        }
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.3,
      "position": [
        624,
        272
      ],
      "id": "370c89d0-27b9-4931-98f5-0af65f76df8c",
      "name": "HTTP Request - Outfit Single"
    }
  ],
  "connections": {},
  "pinData": {},
  "meta": {
    "templateCredsSetupCompleted": true,
    "instanceId": "8e6dcc9cd0896009bb42598fce5a44d1ec101db1299912f392c15fb1c219f4d9"
  }
}
```

## Request Body (formatted)

```json
{
  "images": {
    "hat": "{{ $json.products.hat.url }}",
    "hoodie": "{{ $json.products.hoodie.url }}",
    "pants": "{{ $json.products.pants.url }}",
    "extra": "{{ $json.products.extra.url }}",
    "meme": "{{ $json.products.meme.url }}",
    "shoes": "{{ $json.products.shoes.url }}"
  },
  "main_title": "{{ $json.main_title }}",
  "subtitle": "{{ $json.subtitle }}",
  "title_font_size": 64,
  "subtitle_font_size": 38,
  "response_format": "url"
}
```

## SQL Query (for previous node)

```sql
WITH
  caps AS (SELECT image_url, title FROM product_images WHERE product_type = 'cap' ORDER BY RANDOM() LIMIT 1),
  shirts AS (SELECT image_url, title FROM product_images WHERE product_type IN ('tshirt', 'hoodie') ORDER BY RANDOM() LIMIT 1),
  pants AS (SELECT image_url, title FROM product_images WHERE product_type = 'pants' ORDER BY RANDOM() LIMIT 1),
  memes AS (SELECT image_url, title, ROW_NUMBER() OVER (ORDER BY RANDOM()) as rn FROM product_images WHERE product_type = 'meme'),
  shoes AS (SELECT image_url, title FROM product_images WHERE product_type = 'shoes' ORDER BY RANDOM() LIMIT 1)
SELECT jsonb_build_object(
  'hat', (SELECT jsonb_build_object('url', image_url, 'title', title) FROM caps),
  'hoodie', (SELECT jsonb_build_object('url', image_url, 'title', title) FROM shirts),
  'pants', (SELECT jsonb_build_object('url', image_url, 'title', title) FROM pants),
  'extra', (SELECT jsonb_build_object('url', image_url, 'title', title) FROM memes WHERE rn = 1),
  'meme', (SELECT jsonb_build_object('url', image_url, 'title', title) FROM memes WHERE rn = 2),
  'shoes', (SELECT jsonb_build_object('url', image_url, 'title', title) FROM shoes)
) as products;
```

## Slot Mapping

| Slot | Product Type | Position | Description |
|------|--------------|----------|-------------|
| hat | cap | top center | Caps, kippas, masks, headwear |
| hoodie | tshirt, hoodie | center | Upper body clothing |
| pants | pants | center-lower | Lower body clothing |
| extra | meme | right side | Accessories, props (right) |
| meme | meme | left side | Accessories, props (left) |
| shoes | shoes | bottom | Footwear |
