### search API

- request

```
curl -X GET "https://context7.com/api/v1/search?query=react+hook+form" \
  -H "Authorization: Bearer CONTEXT7_API_KEY"
```

- response

```json
{
  "results": [
    {
      "id": "/react-hook-form/documentation",
      "title": "React Hook Form",
      "description": "📋 Official documentation", 
      "totalTokens": 50275,
      "totalSnippets": 274,
      "stars": 741,
      "trustScore": 9.1,
      "versions": []
    },
    ...
  ]
}
```

### docs API

- request

```
curl -X GET "https://context7.com/api/v1/vercel/next.js?type=txt&topic=ssr&tokens=5000" \
  -H "Authorization: Bearer CONTEXT7_API_KEY"
```

- response

```text
TITLE: Dynamically Load Component Client-Side Only in Next.js Pages Router
DESCRIPTION: Explains how to disable Server-Side Rendering (SSR) for a dynamically...
SOURCE: https://github.com/vercel/next.js/blob/canary/docs/01-app/02-guides/lazy...

LANGUAGE: JSX
CODE:
```
'use client'

import dynamic from 'next/dynamic'

const DynamicHeader = dynamic(() => import('../components/header'), {
  ssr: false,
})
```

----------------------------------------

TITLE: Resolve `Math.random()` SSR Issues with React Suspense in Next.js
DESCRIPTION: This solution demonstrates how to wrap a Client Component that uses...
...
```

### 备注

- CONTEXT7_API_KEY通过环境变量传入LibraryMaster的MCP服务，里面做一个全局变量。发送请求时，从全局变量当中读取。