# Korea Geocoder MCP Server

한국 주소를 위도/경도로 변환하는 MCP (Model Context Protocol) 서버입니다.

## 기능

- 한국 주소를 Google Maps API를 통해 위도/경도로 변환

## 사전 준비

### Google Maps Geocoding API 설정

1. **Google Cloud Console에서 API 키 생성**
   - [Google Cloud Console](https://console.cloud.google.com/)에 접속
   - 새 프로젝트 생성 또는 기존 프로젝트 선택
   - "API 및 서비스" > "라이브러리"로 이동
   - "Geocoding API" 검색 후 활성화
   - "API 및 서비스" > "사용자 인증 정보"로 이동
   - "사용자 인증 정보 만들기" > "API 키" 선택
   - 생성된 API 키 복사

## 사용법

### Claude Desktop에서 사용하기

Claude Desktop에서 MCP 서버를 등록하고 사용할 수 있습니다:
- Claude Desktop의 Settings에서 Developer 섹션으로 이동
- Edit Config를 선택하여 claude_desktop_config.json 파일을 편집합니다.

#### uvx 사용 (권장)
```json
{
  "mcpServers": {
    "korea-geocoder-mcp": {
      "command": "uvx",
      "args": ["korea-geocoder-mcp@latest"],
      "env": {
        "GOOGLE_CLOUD_API_KEY": "발급받은_API_키를_여기에_입력"
      }
    }
  }
}
```

#### 개발 환경
```json
{
  "mcpServers": {
    "korea-geocoder": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/korea-geocoder-mcp",
        "run",
        "korea_geocoder_mcp.geocoder"
      ],
      "env": {
        "GOOGLE_CLOUD_API_KEY": "발급받은_API_키를_여기에_입력"
      }
    }
  }
}
```

- Claude Desktop을 다시 시작합니다.

