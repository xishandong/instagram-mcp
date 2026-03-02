# Instagram MCP Skill

通过 OpenClaw 调用 Instagram MCP 服务，实现 Instagram 数据的搜索和获取。

## 前置条件

### 1. 启动 MCP 服务

确保 Instagram MCP 服务已添加：

```bash
mcporter config add instagram-mcp http://localhost:8000/sse
```

### 2. 检查服务状态

通过健康检查接口确认服务是否正常运行：

```bash
curl http://127.0.0.1:8000/health
```

预期返回：
```json
{
  "status": "ok",
  "server": "instagram-mcp"
}
```

### 3. 配置代理

首次使用前必须配置代理：

```bash
mcporter call 'instagram-mcp.configure(proxy_url:"http://127.0.0.1:7890", headless: true)'
```

## 可用能力

### 1. configure

配置代理和浏览器设置。

**命令**：
```bash
mcporter call 'instagram-mcp.configure(proxy_url:<proxy_url>, headless: <true/false>)'
```

**参数**：
- `proxy_url`: 代理服务器地址（必需）
- `headless`: 是否启用无头模式（可选，默认 true）

**示例**：
```bash
mcporter call 'instagram-mcp.configure(proxy_url:"http://127.0.0.1:7890", headless: true)'
```

**返回值**：
```json
{
  "success": true,
  "message": "Configuration saved successfully. Please restart the MCP server to apply changes.",
  "config": {
    "proxy": {
      "url": "http://127.0.0.1:7890"
    },
    "browser": {
      "headless": false
    }
  }
}
```

### 2. search_users

搜索 Instagram 用户。

**命令**：
```bash
mcporter call 'instagram-mcp.search_users(query: <query>)'
```

**参数**：
- `query`: 用户名或全名（必需）

**示例**：
```bash
mcporter call 'instagram-mcp.search_users(query: "iu")'
```

**返回值**：
```json
{
  "success": true,
  "data": [
    {
      "profile_url": "https://imginn.com/iu2030.official/",
      "avatar_url": "https://s2.imginn.com/556686533_17946789885044067_769798344774827953_n.jpg?t51.82787-15/556686533_17946789885044067_769798344774827953_n.jpg?stp=dst-jpg_e0_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-lga3-1.cdninstagram.com&_nc_cat=103&_nc_oc=Q6cZ2QFRqAPy7mk7lmNnKfiaiGkciAQklBLgddnU9qCnJtdWKwxariaibxeHTJO-KNcQCddpDgdHfu9EnCrJhST8-ghp&_nc_ohc=k5hIIlheTUsQ7kNvwFI-R53&_nc_gid=VWcLeR6RX5nMM4980ScH2w&edm=AIhb9MIBAAAA&ccb=7-5&oh=00_AftQCiLRR4rbtZmV_vm8bta6qX89wxgEG-xFwus1qfp1vQ&oe=69AA4DFB&_nc_sid=8aafe2",
      "alt_text": "@iu2030.official",
      "full_name": "Indiana University Bloomington Class of 2030 (IU ’30)",
      "is_verified": false,
      "username": "iu2030.official"
    }
  ]
}
```

### 3. get_user_profile

获取用户资料信息。

**命令**：
```bash
mcporter call 'instagram-mcp.get_user_profile(username: <username>)'
```

**参数**：
- `username`: Instagram 用户名（必需）

**示例**：
```bash
mcporter call 'instagram-mcp.get_user_profile(username: "dlwlrma")'
```

**返回值**：
```json
{
  "success": true,
  "data": {
    "pk": "1692800026",
    "img": "https://scontent-iad3-1.cdninstagram.com/v/t51.2885-19/425229116_400932362439190_5780921602756818121_n.jpg?stp=dst-jpg_e0_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-iad3-1.cdninstagram.com&_nc_cat=1&_nc_oc=Q6cZ2QHRxiyF9LOvsyvjV9OynQ_J9ZOBsPx88d5bq47A6aVZBy12lTnzjgSrytEsLgzoyD8p9j0ipjiTXYE9y1C5pP4O&_nc_ohc=_Napj5ingrkQ7kNvwFdIJzc&_nc_gid=IEZXBa3hMq4pffHX_AvcCw&edm=ALGbJPMBAAAA&ccb=7-5&oh=00_AftjEgGC7fk5k_d8Eze-61jaefwkrfelGcNliC-Kt_nYmg&oe=6987567F&_nc_sid=7d3ac5",
    "name": "dlwlrma",
    "bio": "The Winning",
    "full_name": "이지금 IU",
    "is_verified": true,
    "followers": 33307964,
    "following": 123,
    "posts": 771
  }
}
```

### 4. get_user_posts

获取用户的帖子列表。

**命令**：
```bash
mcporter call 'instagram-mcp.get_user_posts(_id: <user_id>, cursor: <cursor>)'
```

**参数**：
- `_id`: 用户ID（必需，从 get_user_profile 获取）
- `cursor`: 分页游标（可选，从上一次请求获取）

**示例**：
```bash
# 获取第一页
mcporter call 'instagram-mcp.get_user_posts(_id: "123456789", cursor: "")'

# 获取下一页
mcporter call 'instagram-mcp.get_user_posts(_id: "123456789", cursor: "QVFEMHlsV2M4Yl96QkxaM1BMTUJUaVBEZlZfZmFBakVpcTdGUFk3UDFwYjRmUlhXVWloWlpSdVRSWFNiSGFkQ29rOEJhQmFiMGhjVnpBdFJKNGhwWkNCXw==")'
```

**返回值**：
```json
{
  "success": true,
  "data": {
    "posts": [
      {
        "isPind": false,
        "isSidecar": true,
        "time": "6 days ago",
        "id": "3839447538794129539",
        "code": "DVIdTG7kmiD",
        "likeCount": "2m",
        "commentCount": "6k",
        "alt": "🍓👓✂️💛🌱",
        "accessibility": null,
        "location": null,
        "src": "https://scontent-lga3-3.cdninstagram.com/v/t51.82787-15/641254133_18570022225000027_4405897255883696398_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lga3-3.cdninstagram.com&_nc_cat=1&_nc_oc=Q6cZ2QFQwYQihZMmy6gXwYtr2O5s2jCJSdLu6ymQFHfxcndcfJgWPe35lO0keMOl1wPfw9gbY7Xet8918GqHO4TAl5yh&_nc_ohc=JNHXQvDRrLsQ7kNvwGPXfyv&_nc_gid=loqUZFG5sA27u62vQNHqkg&edm=APU89FABAAAA&ccb=7-5&ig_cache_key=MzgzOTQ0NjYxMDAzMjU5Njg4Mg%3D%3D.3-ccb7-5&oh=00_AfwybKH-S5mzJuxIJeMdq5sRgTrwg51vWq6e2zCg-i272w&oe=69AAE39F&_nc_sid=bc0c2c&dl=1",
        "thumb": "https://s2.imginn.com/641254133_18570022225000027_4405897255883696398_n.jpg?t51.82787-15/641254133_18570022225000027_4405897255883696398_n.jpg?stp=c0.240.1440.1440a_dst-jpg_e35_s640x640_sh0.08_tt6&_nc_ht=scontent-lga3-3.cdninstagram.com&_nc_cat=1&_nc_oc=Q6cZ2QFQwYQihZMmy6gXwYtr2O5s2jCJSdLu6ymQFHfxcndcfJgWPe35lO0keMOl1wPfw9gbY7Xet8918GqHO4TAl5yh&_nc_ohc=JNHXQvDRrLsQ7kNvwGPXfyv&_nc_gid=loqUZFG5sA27u62vQNHqkg&edm=APU89FABAAAA&ccb=7-5&ig_cache_key=MzgzOTQ0NjYxMDAzMjU5Njg4Mg%3D%3D.3.c-ccb7-5&oh=00_AfxriiIft4Lfwtg_sL6JIPWQb-EhhnfemzEimWxPHA_4RA&oe=69AAE39F&_nc_sid=bc0c2c",
        "srcs": [
          "https://scontent-lga3-3.cdninstagram.com/v/t51.82787-15/641254133_18570022225000027_4405897255883696398_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lga3-3.cdninstagram.com&_nc_cat=1&_nc_oc=Q6cZ2QFQwYQihZMmy6gXwYtr2O5s2jCJSdLu6ymQFHfxcndcfJgWPe35lO0keMOl1wPfw9gbY7Xet8918GqHO4TAl5yh&_nc_ohc=JNHXQvDRrLsQ7kNvwGPXfyv&_nc_gid=loqUZFG5sA27u62vQNHqkg&edm=APU89FABAAAA&ccb=7-5&ig_cache_key=MzgzOTQ0NjYxMDAzMjU5Njg4Mg%3D%3D.3-ccb7-5&oh=00_AfwybKH-S5mzJuxIJeMdq5sRgTrwg51vWq6e2zCg-i272w&oe=69AAE39F&_nc_sid=bc0c2c",
          "https://scontent-lga3-3.cdninstagram.com/v/t51.82787-15/641281782_18570022234000027_7499541887766478465_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lga3-3.cdninstagram.com&_nc_cat=1&_nc_oc=Q6cZ2QFQwYQihZMmy6gXwYtr2O5s2jCJSdLu6ymQFHfxcndcfJgWPe35lO0keMOl1wPfw9gbY7Xet8918GqHO4TAl5yh&_nc_ohc=CJB1KqYE5V4Q7kNvwESzqq4&_nc_gid=loqUZFG5sA27u62vQNHqkg&edm=APU89FABAAAA&ccb=7-5&ig_cache_key=MzgzOTQ0NjYxMTg5NDg3OTczNA%3D%3D.3-ccb7-5&oh=00_AfyH88gLjoZLmcQ5TxdYHxoLx6gCvMgBBri2eNTMSISG-Q&oe=69AABB7B&_nc_sid=bc0c2c",
          "https://scontent-lga3-2.cdninstagram.com/v/t51.82787-15/641098417_18570022243000027_5113796914889024112_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lga3-2.cdninstagram.com&_nc_cat=107&_nc_oc=Q6cZ2QFQwYQihZMmy6gXwYtr2O5s2jCJSdLu6ymQFHfxcndcfJgWPe35lO0keMOl1wPfw9gbY7Xet8918GqHO4TAl5yh&_nc_ohc=MwYOCcEG42oQ7kNvwHKsZmY&_nc_gid=loqUZFG5sA27u62vQNHqkg&edm=APU89FABAAAA&ccb=7-5&ig_cache_key=MzgzOTQ0NjYxODI4Njk5MTkxNA%3D%3D.3-ccb7-5&oh=00_AfxMLjCpT54UX2SEzsrxRo0fEg6KkWEZCMO1P4XKt3JywQ&oe=69AAEF21&_nc_sid=bc0c2c",
          "https://scontent-lga3-2.cdninstagram.com/v/t51.82787-15/641751622_18570022252000027_3513237472789199180_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lga3-2.cdninstagram.com&_nc_cat=107&_nc_oc=Q6cZ2QFQwYQihZMmy6gXwYtr2O5s2jCJSdLu6ymQFHfxcndcfJgWPe35lO0keMOl1wPfw9gbY7Xet8918GqHO4TAl5yh&_nc_ohc=8d5NufcWGmAQ7kNvwGgte6b&_nc_gid=loqUZFG5sA27u62vQNHqkg&edm=APU89FABAAAA&ccb=7-5&ig_cache_key=MzgzOTQ0NjYyNDY3MDcxMzkyMQ%3D%3D.3-ccb7-5&oh=00_Afz7PtYt-e1FpJ2Q81EHD8w4iUlYt5rzTz4vvnEY3Qs4yg&oe=69AAD8E6&_nc_sid=bc0c2c",
          "https://scontent-lga3-2.cdninstagram.com/v/t51.82787-15/638840336_18570022261000027_8278666962744478157_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lga3-2.cdninstagram.com&_nc_cat=107&_nc_oc=Q6cZ2QFQwYQihZMmy6gXwYtr2O5s2jCJSdLu6ymQFHfxcndcfJgWPe35lO0keMOl1wPfw9gbY7Xet8918GqHO4TAl5yh&_nc_ohc=km8fgL0dzm8Q7kNvwGRb_1b&_nc_gid=loqUZFG5sA27u62vQNHqkg&edm=APU89FABAAAA&ccb=7-5&ig_cache_key=MzgzOTQ0NjYyNzY5MDY0MDY4MQ%3D%3D.3-ccb7-5&oh=00_AfzcBDkOz1iFbbo-HmORlg4MqU7L2x2y4kPDuy81KBwqrQ&oe=69AAD21C&_nc_sid=bc0c2c",
          "https://scontent-lga3-2.cdninstagram.com/v/t51.82787-15/638898382_18570022270000027_3877070507691691099_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lga3-2.cdninstagram.com&_nc_cat=107&_nc_oc=Q6cZ2QFQwYQihZMmy6gXwYtr2O5s2jCJSdLu6ymQFHfxcndcfJgWPe35lO0keMOl1wPfw9gbY7Xet8918GqHO4TAl5yh&_nc_ohc=3zm-PpSnqSIQ7kNvwHCw_cf&_nc_gid=loqUZFG5sA27u62vQNHqkg&edm=APU89FABAAAA&ccb=7-5&ig_cache_key=MzgzOTQ0NjYyOTE4Mzg0NzkyMg%3D%3D.3-ccb7-5&oh=00_AfyVf-sJ5nRCYwwbwZjnrMTfOczCIryHwaC4_NmFqcIcDQ&oe=69AAE552&_nc_sid=bc0c2c",
          "https://scontent-lga3-2.cdninstagram.com/v/t51.82787-15/635098535_18570022279000027_4005142160235005734_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lga3-2.cdninstagram.com&_nc_cat=107&_nc_oc=Q6cZ2QFQwYQihZMmy6gXwYtr2O5s2jCJSdLu6ymQFHfxcndcfJgWPe35lO0keMOl1wPfw9gbY7Xet8918GqHO4TAl5yh&_nc_ohc=7AX6n78AvNoQ7kNvwGZk_za&_nc_gid=loqUZFG5sA27u62vQNHqkg&edm=APU89FABAAAA&ccb=7-5&ig_cache_key=MzgzOTQ0NjYzMjc1NzM3MTY0MA%3D%3D.3-ccb7-5&oh=00_Afw_oQBjNhum8jXZOYnTdePDQtto-igoUL7okFTNYfJwbg&oe=69AAC6B6&_nc_sid=bc0c2c",
          "https://scontent-lga3-2.cdninstagram.com/v/t51.82787-15/637757403_18570022288000027_8050030411694449409_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lga3-2.cdninstagram.com&_nc_cat=107&_nc_oc=Q6cZ2QFQwYQihZMmy6gXwYtr2O5s2jCJSdLu6ymQFHfxcndcfJgWPe35lO0keMOl1wPfw9gbY7Xet8918GqHO4TAl5yh&_nc_ohc=TRdp4xrWf7oQ7kNvwEUhlAQ&_nc_gid=loqUZFG5sA27u62vQNHqkg&edm=APU89FABAAAA&ccb=7-5&ig_cache_key=MzgzOTQ0NjYzMzUyOTExNzczMg%3D%3D.3-ccb7-5&oh=00_Afw_vF3Hxsttd-TedblV9iii8W5S0FXdmt6Afdar4AY3fg&oe=69AAD7FC&_nc_sid=bc0c2c",
          "https://scontent-lga3-2.cdninstagram.com/v/t51.82787-15/641944475_18570022297000027_752468402572244398_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lga3-2.cdninstagram.com&_nc_cat=107&_nc_oc=Q6cZ2QFQwYQihZMmy6gXwYtr2O5s2jCJSdLu6ymQFHfxcndcfJgWPe35lO0keMOl1wPfw9gbY7Xet8918GqHO4TAl5yh&_nc_ohc=0dkSThbU7ZIQ7kNvwFK5UqO&_nc_gid=loqUZFG5sA27u62vQNHqkg&edm=APU89FABAAAA&ccb=7-5&ig_cache_key=MzgzOTQ0NjYzNjM3Mjg0MDM3Ng%3D%3D.3-ccb7-5&oh=00_Afxj3l_vMacDXNrhd8nJmV8FRZtkhmc3SJoCHEXxGDRQsQ&oe=69AAEABC&_nc_sid=bc0c2c",
          "https://scontent-lga3-2.cdninstagram.com/v/t51.82787-15/642138247_18570022306000027_297879275666571047_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lga3-2.cdninstagram.com&_nc_cat=107&_nc_oc=Q6cZ2QFQwYQihZMmy6gXwYtr2O5s2jCJSdLu6ymQFHfxcndcfJgWPe35lO0keMOl1wPfw9gbY7Xet8918GqHO4TAl5yh&_nc_ohc=e_JZTgKujkMQ7kNvwEd9tqM&_nc_gid=loqUZFG5sA27u62vQNHqkg&edm=APU89FABAAAA&ccb=7-5&ig_cache_key=MzgzOTQ0NjYzOTgzNzM3OTMzMQ%3D%3D.3-ccb7-5&oh=00_AfxC5tDND1TXdswcu6OQTb4hrnJAJdXIm6mdY7S8lj0xdg&oe=69AABD1C&_nc_sid=bc0c2c",
          "https://scontent-lga3-2.cdninstagram.com/v/t51.82787-15/640625870_18570022315000027_9022788455784254644_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lga3-2.cdninstagram.com&_nc_cat=107&_nc_oc=Q6cZ2QFQwYQihZMmy6gXwYtr2O5s2jCJSdLu6ymQFHfxcndcfJgWPe35lO0keMOl1wPfw9gbY7Xet8918GqHO4TAl5yh&_nc_ohc=9FyrXoUr9p4Q7kNvwEjTasO&_nc_gid=loqUZFG5sA27u62vQNHqkg&edm=APU89FABAAAA&ccb=7-5&ig_cache_key=MzgzOTQ0NjY0MDM1NzQ3MDg2Ng%3D%3D.3-ccb7-5&oh=00_AfzuWT5whUoiIcpvtGXaerUz0jEe0SKgy5MpH5-d2VGiwQ&oe=69AAC716&_nc_sid=bc0c2c",
          "https://scontent-lga3-2.cdninstagram.com/v/t51.82787-15/638863408_18570022324000027_5976845761388332742_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lga3-2.cdninstagram.com&_nc_cat=107&_nc_oc=Q6cZ2QFQwYQihZMmy6gXwYtr2O5s2jCJSdLu6ymQFHfxcndcfJgWPe35lO0keMOl1wPfw9gbY7Xet8918GqHO4TAl5yh&_nc_ohc=-r2uPLeVxKUQ7kNvwHh5Pca&_nc_gid=loqUZFG5sA27u62vQNHqkg&edm=APU89FABAAAA&ccb=7-5&ig_cache_key=MzgzOTQ0NjY0NDYzNTYyMDYxNw%3D%3D.3-ccb7-5&oh=00_AfwPvhzkR5QId3sllhm40C3vFgEBZpLZxgVEAyWFQ4qIlA&oe=69AAEE0E&_nc_sid=bc0c2c",
          "https://scontent-lga3-2.cdninstagram.com/v/t51.82787-15/640417901_18570022339000027_1224346407623616247_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lga3-2.cdninstagram.com&_nc_cat=107&_nc_oc=Q6cZ2QFQwYQihZMmy6gXwYtr2O5s2jCJSdLu6ymQFHfxcndcfJgWPe35lO0keMOl1wPfw9gbY7Xet8918GqHO4TAl5yh&_nc_ohc=DJZJpjughkYQ7kNvwGh8Cmz&_nc_gid=loqUZFG5sA27u62vQNHqkg&edm=APU89FABAAAA&ccb=7-5&ig_cache_key=MzgzOTQ0NjY0ODIwMDc4NTU1OA%3D%3D.3-ccb7-5&oh=00_Afwfik5x7pJ0zcqa-31dE2HpFBNGXuRUSmDqZjc8yNA9Hg&oe=69AAC4BA&_nc_sid=bc0c2c",
          "https://scontent-lga3-2.cdninstagram.com/v/t51.82787-15/639824545_18570022342000027_2934327155550613375_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lga3-2.cdninstagram.com&_nc_cat=107&_nc_oc=Q6cZ2QFQwYQihZMmy6gXwYtr2O5s2jCJSdLu6ymQFHfxcndcfJgWPe35lO0keMOl1wPfw9gbY7Xet8918GqHO4TAl5yh&_nc_ohc=zNG_P0olw00Q7kNvwF22Kh8&_nc_gid=loqUZFG5sA27u62vQNHqkg&edm=APU89FABAAAA&ccb=7-5&ig_cache_key=MzgzOTQ0NjY0Nzg4MTk5MzI4NA%3D%3D.3-ccb7-5&oh=00_AfzyVWZCIa10vc8krw3KSLPmLCfGvJMJUBf7Zi5Arxot9g&oe=69AAC86E&_nc_sid=bc0c2c",
          "https://scontent-lga3-2.cdninstagram.com/v/t51.82787-15/640192300_18570022351000027_5277114231674099924_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lga3-2.cdninstagram.com&_nc_cat=107&_nc_oc=Q6cZ2QFQwYQihZMmy6gXwYtr2O5s2jCJSdLu6ymQFHfxcndcfJgWPe35lO0keMOl1wPfw9gbY7Xet8918GqHO4TAl5yh&_nc_ohc=a7C5hxg0A1QQ7kNvwHNW5kl&_nc_gid=loqUZFG5sA27u62vQNHqkg&edm=APU89FABAAAA&ccb=7-5&ig_cache_key=MzgzOTQ0NjY1MTQ4MDc2NDk5NQ%3D%3D.3-ccb7-5&oh=00_Afxrm7lFyqIVAa-kwIhfmWqnrh3GhyTG-HZ1YW1-96QqOw&oe=69AAE32D&_nc_sid=bc0c2c",
          "https://scontent-lga3-2.cdninstagram.com/v/t51.82787-15/636687409_18570022360000027_2780323073555247234_n.jpg?stp=dst-jpg_e35_p1080x1080_sh0.08_tt6&_nc_ht=scontent-lga3-2.cdninstagram.com&_nc_cat=107&_nc_oc=Q6cZ2QFQwYQihZMmy6gXwYtr2O5s2jCJSdLu6ymQFHfxcndcfJgWPe35lO0keMOl1wPfw9gbY7Xet8918GqHO4TAl5yh&_nc_ohc=WURz-p5yNTcQ7kNvwH6DKwf&_nc_gid=loqUZFG5sA27u62vQNHqkg&edm=APU89FABAAAA&ccb=7-5&ig_cache_key=MzgzOTQ0NjY1Mzc3OTE4OTg3MQ%3D%3D.3-ccb7-5&oh=00_Afw1EedWE3GeaF-u0uioOLp9uhtRjxnXp-QXL5oSlp1sng&oe=69AAD088&_nc_sid=bc0c2c"
        ],
        "date": 1771917835
      }
    ],
    "cursor": "QVFEMHlsV2M4Yl96QkxaM1BMTUJUaVBEZlZfZmFBakVpcTdGUFk3UDFwYjRmUlhXVWloWlpSdVRSWFNiSGFkQ29rOEJhQmFiMGhjVnpBdFJKNGhwWkNCXw==",
    "hasNext": true,
    "_id": "1692800026"
  }
}
```

### 5. get_post_details

获取帖子详细信息。

**命令**：
```bash
mcporter call 'instagram-mcp.get_post_details(post_shortcode: <shortcode>)'
```

**参数**：
- `post_shortcode`: 帖子短代码（必需，URL中 `/p/` 后面的部分）

**示例**：
```bash
mcporter call 'instagram-mcp.get_post_details(post_shortcode: "DVIdTG7kmiD")'
```

**返回值**：
```json
{
  "success": true,
  "data": {
    "post_url": "https://imginn.com/p/DVIdTG7kmiD/",
    "images": [
      "https://scontent-ord5-1.cdninstagram.com/v/t51.82787-15/641254133_18570022225000027_4405897255883696398_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=101&ig_cache_key=MzgzOTQ0NjYxMDAzMjU5Njg4Mg%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&_nc_aid=0&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjE0NDB4MTkyMC5zZHIuQzMifQ%3D%3D&_nc_ohc=RaDCe9c67msQ7kNvwH5aDkc&_nc_oc=AdmyYUwRED-22vpTiMRk0KfFm2YvvXxImbI-nXGzY91fySukB8bVX9LjAI7jDQSwBa0N5bSIV7BSa0ZkcV7req26&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=7&_nc_ht=scontent-ord5-1.cdninstagram.com&_nc_gid=AIvxuSq3Z2tOwraPOL7tvQ&_nc_ss=8&oh=00_AfzoZkHlwD17Dgty3Z40MUIZubXKudmddc7ngD2l6yGo_w&oe=69AAE39F",
      "https://scontent-ord5-3.cdninstagram.com/v/t51.82787-15/641281782_18570022234000027_7499541887766478465_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=106&ig_cache_key=MzgzOTQ0NjYxMTg5NDg3OTczNA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&_nc_aid=0&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjE0NDB4MTkyMC5zZHIuQzMifQ%3D%3D&_nc_ohc=C_BKvfat5YMQ7kNvwFyW8WY&_nc_oc=AdkUeiZA5EIccSN5CYfK4lOgPEL5GLVk2r5EElyZd9vvAtV-5eBTyfrjOJHsRNjSubsydFeS24jtR7l1vV4PNfwR&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=7&_nc_ht=scontent-ord5-3.cdninstagram.com&_nc_gid=AIvxuSq3Z2tOwraPOL7tvQ&_nc_ss=8&oh=00_AfxjwsmfOIWPJT_eorzkN7hA9w8HOInWPLRk6s_azYDebQ&oe=69AAF3BB",
      "https://scontent-ord5-2.cdninstagram.com/v/t51.82787-15/641098417_18570022243000027_5113796914889024112_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=104&ig_cache_key=MzgzOTQ0NjYxODI4Njk5MTkxNA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&_nc_aid=0&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjE0NDB4MTkyMC5zZHIuQzMifQ%3D%3D&_nc_ohc=oWmJnxDwqD0Q7kNvwGQGXiE&_nc_oc=AdmLqruwAGbXrOIAdRYMpiLvzy9GIiGGUVUKKOLngpwZ5KhFMpLFvLQRlEOzKN6GkyyuaxB2qDZO8dJEc9cR-PA-&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=7&_nc_ht=scontent-ord5-2.cdninstagram.com&_nc_gid=AIvxuSq3Z2tOwraPOL7tvQ&_nc_ss=8&oh=00_AfwTQWKQH0nj2e8SPAano6k3_JSyZO7ATpHn6OarRvb5vw&oe=69AAEF21",
      "https://scontent-ord5-2.cdninstagram.com/v/t51.82787-15/641751622_18570022252000027_3513237472789199180_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=105&ig_cache_key=MzgzOTQ0NjYyNDY3MDcxMzkyMQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&_nc_aid=0&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjE0NDB4MTkxMC5zZHIuQzMifQ%3D%3D&_nc_ohc=bqCtG6cbJVMQ7kNvwFx0_H9&_nc_oc=AdnWqY9KyIXpxJKYowrtvAZNGqr4pY0dWUCT2Zdch63TmZJePZGUzQq7SaWdoVJiS79CAQHGpQSHKYk63VTKQXns&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=7&_nc_ht=scontent-ord5-2.cdninstagram.com&_nc_gid=AIvxuSq3Z2tOwraPOL7tvQ&_nc_ss=8&oh=00_AfyQLQfuIDbDKEF4UW1IyFB8e_3hCvxBvXmkDZAjg51ZXQ&oe=69AAD8E6",
      "https://scontent-ord5-3.cdninstagram.com/v/t51.82787-15/638840336_18570022261000027_8278666962744478157_n.jpg?stp=dst-jpegr_e35_tt6&_nc_cat=109&ig_cache_key=MzgzOTQ0NjYyNzY5MDY0MDY4MQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&_nc_aid=0&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjE0NDB4MTkxMC5oZHIuQzMifQ%3D%3D&_nc_ohc=kXG99pCIb3gQ7kNvwGhf9OC&_nc_oc=AdlNdiZhPvyzDztwWWGiHwZKvCWlUnXeb46YHFH54kdZKo40ixDsgJdXTRCvLdHEZgYvvUOcnYfA1vrmKlMQSEpw&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=7&_nc_ht=scontent-ord5-3.cdninstagram.com&_nc_gid=AIvxuSq3Z2tOwraPOL7tvQ&_nc_ss=8&oh=00_AfzIk2qeKHQJ47W69K643YTauZfxrX27Ll2XQTneCCcp8w&oe=69AAD21C",
      "https://scontent-ord5-3.cdninstagram.com/v/t51.82787-15/638898382_18570022270000027_3877070507691691099_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=109&ig_cache_key=MzgzOTQ0NjYyOTE4Mzg0NzkyMg%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&_nc_aid=0&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjEyODB4MTY5Ny5zZHIuQzMifQ%3D%3D&_nc_ohc=vB_G11gT0AQQ7kNvwHg4po5&_nc_oc=AdlnX5hVfWAYYgL2DS1uOk_EbAMzhcShJOT6_QLKecz_SkYB2RrdDLT2ZR4SuYXY9KUTE7IY3AOa0lmCmTkxa3pE&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=7&_nc_ht=scontent-ord5-3.cdninstagram.com&_nc_gid=AIvxuSq3Z2tOwraPOL7tvQ&_nc_ss=8&oh=00_AfzZmSvWGfgIxQE3CAt1SbnHDHdg7y7OulEd8n6Ap--Eig&oe=69AAE552",
      "https://scontent-ord5-2.cdninstagram.com/v/t51.82787-15/635098535_18570022279000027_4005142160235005734_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=105&ig_cache_key=MzgzOTQ0NjYzMjc1NzM3MTY0MA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&_nc_aid=0&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjE0NDB4MTkyMC5zZHIuQzMifQ%3D%3D&_nc_ohc=A9aqLdybOW0Q7kNvwGmMd68&_nc_oc=AdlKatLAG0P11U-wC3cuXqvAzbTUWC2ISaZLTi4_hw6dFJ5IdBQqkwcOs1KtHE5Adwe8VO4-LE03tLM07LKcgelQ&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=7&_nc_ht=scontent-ord5-2.cdninstagram.com&_nc_gid=AIvxuSq3Z2tOwraPOL7tvQ&_nc_ss=8&oh=00_AfzoF7YcPvpJsjoKF7FxBERZ3nztcFzrcAFvESRLGjeMHQ&oe=69AAC6B6",
      "https://scontent-ord5-3.cdninstagram.com/v/t51.82787-15/637757403_18570022288000027_8050030411694449409_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=110&ig_cache_key=MzgzOTQ0NjYzMzUyOTExNzczMg%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&_nc_aid=0&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjE0NDB4MTkyMC5zZHIuQzMifQ%3D%3D&_nc_ohc=RuIG_C5whbkQ7kNvwGUXdu3&_nc_oc=Adn9D4GD45cwjtl4zpaY_eyIgsm2m4jm-vMvro1JwVEIzWHTUYBpRLXGQBQOausyAg2you7zMTWGXzekR8ClWaqx&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=7&_nc_ht=scontent-ord5-3.cdninstagram.com&_nc_gid=AIvxuSq3Z2tOwraPOL7tvQ&_nc_ss=8&oh=00_AfzSvsqiJd73pmKRC3aCrIinUg3oaJjjuAIeFHGXznuznA&oe=69AAD7FC",
      "https://scontent-ord5-2.cdninstagram.com/v/t51.82787-15/641944475_18570022297000027_752468402572244398_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=103&ig_cache_key=MzgzOTQ0NjYzNjM3Mjg0MDM3Ng%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&_nc_aid=0&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjE0NDB4MTkyMC5zZHIuQzMifQ%3D%3D&_nc_ohc=H2jQ7M1YM3sQ7kNvwFumPOl&_nc_oc=AdlxysBdn4t9g5B48CQb2320OfKm4AF2RsbiJuiGiCY-uvyuSmPgyzeaxF59XEZH1jyMe4glOVkQeIH7-33538ny&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=7&_nc_ht=scontent-ord5-2.cdninstagram.com&_nc_gid=AIvxuSq3Z2tOwraPOL7tvQ&_nc_ss=8&oh=00_AfwEav8ZNVNTLwwatIfGmY5SKZAqRL8f_BgG9jLDJWQwlA&oe=69AAEABC",
      "https://scontent-ord5-3.cdninstagram.com/v/t51.82787-15/642138247_18570022306000027_297879275666571047_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=106&ig_cache_key=MzgzOTQ0NjYzOTgzNzM3OTMzMQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&_nc_aid=0&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjE0NDB4MTkyMC5zZHIuQzMifQ%3D%3D&_nc_ohc=juaDFqGkcB4Q7kNvwHnKDte&_nc_oc=AdkRD7VBy6RkJ5js3fUPuP0wkZZC540QY1rzKa9ieVpxOZ9TDrCYvbbI4l8MPOkQVVSvrgSzim0ikg4yM0ZbBTtM&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=7&_nc_ht=scontent-ord5-3.cdninstagram.com&_nc_gid=AIvxuSq3Z2tOwraPOL7tvQ&_nc_ss=8&oh=00_AfxF0qpTKvZOUUMOY9vkEtx3GCQk3hPpVjfRtakYGFtHlA&oe=69AABD1C",
      "https://scontent-ord5-1.cdninstagram.com/v/t51.82787-15/640625870_18570022315000027_9022788455784254644_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=108&ig_cache_key=MzgzOTQ0NjY0MDM1NzQ3MDg2Ng%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&_nc_aid=0&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjE0NDB4MTkyMC5zZHIuQzMifQ%3D%3D&_nc_ohc=Bqtu1YOeXikQ7kNvwEIKU7V&_nc_oc=AdmKmFwGUfT5O2Q57pW3odzjF2pdGewPp2zkWzAXiSjfH0qihfaUseUNqvhZ5aFozZAOfuypD1XyG6uVEj9DDeSx&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=7&_nc_ht=scontent-ord5-1.cdninstagram.com&_nc_gid=AIvxuSq3Z2tOwraPOL7tvQ&_nc_ss=8&oh=00_Afw6o6A0cJEddIDAoWRlB4FqKu-LDkDH8dxHLEqhCLRS7g&oe=69AAC716",
      "https://scontent-ord5-3.cdninstagram.com/v/t51.82787-15/638863408_18570022324000027_5976845761388332742_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=106&ig_cache_key=MzgzOTQ0NjY0NDYzNTYyMDYxNw%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&_nc_aid=0&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjE0NDB4MTkxMC5zZHIuQzMifQ%3D%3D&_nc_ohc=NwuM6AW-UTIQ7kNvwEaJvuY&_nc_oc=AdlQOS__OxEnrjl6KVK8M6DRVswsEIWZ7H_KJwGk7J19UXjeX0sGsHKUGI1J48vx_kn28tHIH3T0xUPqa4jCbZQ5&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=7&_nc_ht=scontent-ord5-3.cdninstagram.com&_nc_gid=AIvxuSq3Z2tOwraPOL7tvQ&_nc_ss=8&oh=00_AfwsdMCU8Gpj7J2zQHHScar9tKP-XSQroD5JPjNQbq4P6A&oe=69AAEE0E",
      "https://scontent-ord5-3.cdninstagram.com/v/t51.82787-15/640417901_18570022339000027_1224346407623616247_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=100&ig_cache_key=MzgzOTQ0NjY0ODIwMDc4NTU1OA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&_nc_aid=0&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjE0NDB4MTkxMC5zZHIuQzMifQ%3D%3D&_nc_ohc=shJuUKgWJFAQ7kNvwE-vcDC&_nc_oc=Adl9llAC0QdvTw_d-CFjKXypt3dCMuOUie3WlF-Zp9QPS4s4S4EvBHOP9b4E_uZ6jscniy2TWDX_fjhTkNQ9Z4vH&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=7&_nc_ht=scontent-ord5-3.cdninstagram.com&_nc_gid=AIvxuSq3Z2tOwraPOL7tvQ&_nc_ss=8&oh=00_AfyqsLswqm-YwViEiv5bhRE2wwsIq0uzOkmZMKBNqRWTXg&oe=69AAC4BA",
      "https://scontent-ord5-3.cdninstagram.com/v/t51.82787-15/639824545_18570022342000027_2934327155550613375_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=110&ig_cache_key=MzgzOTQ0NjY0Nzg4MTk5MzI4NA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&_nc_aid=0&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjE0NDB4MTkxMC5zZHIuQzMifQ%3D%3D&_nc_ohc=pf-1h6CrxEsQ7kNvwFGASJm&_nc_oc=Adn3RcYeEPwk7A24e_6Bit-5zbJJu5BDDYowSnr-z6cgz6_2qYpX8AHe7DkPHqGhjkyDmgkh6Cs3N2YYa25I2Fb8&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=7&_nc_ht=scontent-ord5-3.cdninstagram.com&_nc_gid=AIvxuSq3Z2tOwraPOL7tvQ&_nc_ss=8&oh=00_AfzjudfW0S0rUkGV2CvxG0PIaXWG62-eILDUuakMTBMyzQ&oe=69AAC86E",
      "https://scontent-ord5-1.cdninstagram.com/v/t51.82787-15/640192300_18570022351000027_5277114231674099924_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=111&ig_cache_key=MzgzOTQ0NjY1MTQ4MDc2NDk5NQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&_nc_aid=0&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjE0NDB4MTkyMC5zZHIuQzMifQ%3D%3D&_nc_ohc=G4NY955Yz6oQ7kNvwEAKUFK&_nc_oc=AdkhS4ywCFgk7opWzGxtiJLT5zlmiUdqJUJ9c17IdZ3qdLucdsbe3QPSE4eu1LULckamF4MycqjdE-snPOXpTxCe&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=7&_nc_ht=scontent-ord5-1.cdninstagram.com&_nc_gid=AIvxuSq3Z2tOwraPOL7tvQ&_nc_ss=8&oh=00_AfxZHsjkuzodvpbZbjuE4tJlYIg6Ya5KUBDvyxRxvPwPpA&oe=69AAE32D",
      "https://scontent-ord5-2.cdninstagram.com/v/t51.82787-15/636687409_18570022360000027_2780323073555247234_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=105&ig_cache_key=MzgzOTQ0NjY1Mzc3OTE4OTg3MQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&_nc_aid=0&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjExNzB4MTU2MC5zZHIuQzMifQ%3D%3D&_nc_ohc=nzrPKwJrEs0Q7kNvwHlyVEy&_nc_oc=AdkORjQs5c4psUdpDC_nQcqmHYzKtlug_HR74lQQWtRzXiHAzJ22r52D77slo-7IdUIPXl9li8W6jfceh8_WdKun&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=7&_nc_ht=scontent-ord5-2.cdninstagram.com&_nc_gid=AIvxuSq3Z2tOwraPOL7tvQ&_nc_ss=8&oh=00_AfwueUSYe70UMBnfI6ff7w-mikIB5mWjUryyiirNrES6dA&oe=69AAD088"
    ],
    "video_url": null,
    "likes": 1603974,
    "comments": 6459,
    "user_info": {
      "username": "dlwlrma",
      "fullname": "이지금 IU",
      "profile_url": "https://imginn.com/dlwlrma/"
    },
    "tagged_users": [],
    "post_content": "🍓👓✂️💛🌱",
    "timestamp": "February 24th 2026, 07:23 am",
    "post_type": "image"
  }
}
```

### 6. close_browser

手动关闭浏览器实例以释放资源。

**命令**：
```bash
mcporter call 'instagram-mcp.close_browser()'
```

**参数**：无

**示例**：
```bash
mcporter call 'instagram-mcp.close_browser()'
```

**返回值**：
```json
{
  "success": true,
  "message": "Browser closed successfully. It will be automatically reopened on the next request."
}
```

## 典型使用流程

### 1. 配置代理

```bash
# 检查服务状态
curl http://127.0.0.1:8000/health

# 配置代理
mcporter call 'instagram-mcp.configure(proxy_url:"http://127.0.0.1:7890", headless: true)'
```

### 2. 搜索用户

```bash
mcporter call 'instagram-mcp.search_users(query: "iu")'
```

### 3. 获取用户资料

```bash
mcporter call 'instagram-mcp.get_user_profile(username: "dlwlrma")'
```

### 4. 获取用户帖子

```bash
# 获取第一页
mcporter call 'instagram-mcp.get_user_posts(_id: "123456789", cursor: "")'

# 获取下一页
mcporter call 'instagram-mcp.get_user_posts(_id: "123456789", cursor: "QVFEMHlsV2M4Yl96QkxaM1BMTUJUaVBEZlZfZmFBakVpcTdGUFk3UDFwYjRmUlhXVWloWlpSdVRSWFNiSGFkQ29rOEJhQmFiMGhjVnpBdFJKNGhwWkNCXw==")'
```

### 5. 获取帖子详情

```bash
mcporter call 'instagram-mcp.get_post_details(post_shortcode: "DVIdTG7kmiD")'
```

### 6. 释放资源

```bash
mcporter call 'instagram-mcp.close_browser()'
```

## 注意事项

1. **代理配置**: 必须先配置代理才能使用 Instagram 相关功能
2. **服务检查**: 使用前确保服务正常运行
3. **分页查询**: 获取帖子列表时，使用返回的 cursor 进行分页
4. **资源管理**: 使用完毕后可调用 close_browser 释放资源
5. **配置热更新**: 代理配置更新后无需重启服务，自动应用新配置
6. **资源释放**: 在一组操作完成后，调用 close_browser 释放资源，切记！一定要释放资源，否则会导致资源泄漏
## 错误处理

### 代理未配置

```json
{
  "success": false,
  "error": "Proxy not configured. Please use the 'configure' tool first to set up your proxy settings.",
  "message": "Instagram access requires a proxy to work properly. Please configure your proxy settings."
}
```
