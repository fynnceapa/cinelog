# CineLog - REST API Documentation

## Overview
API-ul REST al CineLog urmează principiile RESTful și oferă acces complet la resursele aplicației.

## Base URL
```
http://localhost:8000/api/
```

## Authentication
API-ul suportă următoarele metode de autentificare:
- **OIDC Authentication** (Mozilla Django OIDC)
- **Session Authentication** (pentru web)
- **Basic Authentication** (pentru testare)

Includere header:
```
Authorization: Bearer <token>
```

## Response Format
Toate răspunsurile sunt în format JSON. Status codes HTTP standard sunt utilizate:
- `200 OK` - Succes
- `201 Created` - Resursă creată
- `204 No Content` - Succes fără conținut
- `400 Bad Request` - Eroare validare
- `401 Unauthorized` - Autentificare necesară
- `403 Forbidden` - Permisiune refuzată
- `404 Not Found` - Resursă nu găsită
- `500 Internal Server Error` - Eroare server

## Pagination
Listele sunt paginate cu 10 elemente per pagină:
```
GET /api/movies/?page=1
```

Răspuns:
```json
{
  "count": 50,
  "next": "http://localhost:8000/api/movies/?page=2",
  "previous": null,
  "results": [...]
}
```

## Filtering, Searching, and Ordering
Suportă filtrare, căutare și sortare parametrizată:

### Filtering
```
GET /api/movies/?rating=4.0
GET /api/movies/?release_date=2024-01-01
```

### Searching
```
GET /api/movies/?search=avatar
GET /api/reviews/?search=john
```

### Ordering
```
GET /api/movies/?ordering=rating
GET /api/movies/?ordering=-created_at
```

---

## Endpoints

### 1. Movies

#### GET /api/movies/
Listează toate filmele
```bash
curl http://localhost:8000/api/movies/
```

**Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "title": "Avatar",
      "description": "Film de science fiction",
      "release_date": "2024-01-01",
      "poster_url": "https://...",
      "rating": 4.5,
      "review_count": 12,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### GET /api/movies/{id}/
Obține detalii film specific
```bash
curl http://localhost:8000/api/movies/1/
```

#### POST /api/movies/
Crează un nou film (necesită autentificare)
```bash
curl -X POST http://localhost:8000/api/movies/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Avatar 2",
    "description": "Continuarea...",
    "release_date": "2024-12-20",
    "poster_url": "https://..."
  }'
```

#### PUT /api/movies/{id}/
Actualizează film (necesită autentificare)
```bash
curl -X PUT http://localhost:8000/api/movies/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Avatar (Updated)"}'
```

#### DELETE /api/movies/{id}/
Șterge film (necesită autentificare)
```bash
curl -X DELETE http://localhost:8000/api/movies/1/ \
  -H "Authorization: Bearer <token>"
```

#### GET /api/movies/top_rated/
Top 10 filme după rating
```bash
curl http://localhost:8000/api/movies/top_rated/
```

#### GET /api/movies/popular/
Top 10 filme după numărul de recenzii
```bash
curl http://localhost:8000/api/movies/popular/
```

---

### 2. Reviews

#### GET /api/reviews/
Listează toate recenziile
```bash
curl http://localhost:8000/api/reviews/
```

**Response:**
```json
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "user": 1,
      "user_id": 1,
      "username": "john_doe",
      "movie": 1,
      "movie_title": "Avatar",
      "rating": 5,
      "content": "Film excelent!",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### GET /api/reviews/{id}/
Obține detalii recenzie
```bash
curl http://localhost:8000/api/reviews/1/
```

#### POST /api/reviews/
Crează o nouă recenzie (necesită autentificare)
```bash
curl -X POST http://localhost:8000/api/reviews/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "movie": 1,
    "rating": 4,
    "content": "Film foarte bun!"
  }'
```

#### PUT /api/reviews/{id}/
Actualizează recenzie proprie (necesită autentificare)
```bash
curl -X PUT http://localhost:8000/api/reviews/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"rating": 5}'
```

#### DELETE /api/reviews/{id}/
Șterge recenzie proprie (necesită autentificare)
```bash
curl -X DELETE http://localhost:8000/api/reviews/1/ \
  -H "Authorization: Bearer <token>"
```

#### GET /api/reviews/?movie_id={movie_id}
Obține recenziile unui film specific
```bash
curl http://localhost:8000/api/reviews/?movie_id=1
```

---

### 3. Users

#### GET /api/users/
Listează toți utilizatorii
```bash
curl http://localhost:8000/api/users/
```

**Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "date_joined": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### GET /api/users/{id}/
Obține detalii utilizator
```bash
curl http://localhost:8000/api/users/1/
```

---

### 4. User Profiles

#### GET /api/profiles/
Listează toate profilurile
```bash
curl http://localhost:8000/api/profiles/
```

**Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com"
      },
      "bio": "Iubitor de filme",
      "avatar_url": "https://...",
      "followed_by_count": 5,
      "follows_count": 10
    }
  ]
}
```

#### GET /api/profiles/{id}/
Obține detalii profil
```bash
curl http://localhost:8000/api/profiles/1/
```

#### PUT /api/profiles/{id}/
Actualizează profil propriu (necesită autentificare)
```bash
curl -X PUT http://localhost:8000/api/profiles/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Pasionat de SF",
    "avatar_url": "https://..."
  }'
```

#### POST /api/profiles/{id}/follow/
Urmărește un utilizator (necesită autentificare)
```bash
curl -X POST http://localhost:8000/api/profiles/1/follow/ \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{"message": "Urmărire reușită"}
```

#### POST /api/profiles/{id}/unfollow/
Încetează urmărirea unui utilizator (necesită autentificare)
```bash
curl -X POST http://localhost:8000/api/profiles/1/unfollow/ \
  -H "Authorization: Bearer <token>"
```

#### GET /api/profiles/{id}/followers/
Obține lista urmăritorilor
```bash
curl http://localhost:8000/api/profiles/1/followers/
```

#### GET /api/profiles/{id}/following/
Obține lista persoanelor urmărite
```bash
curl http://localhost:8000/api/profiles/1/following/
```

---

### 5. Watchlist

#### GET /api/watchlist/
Obține watchlist-ul utilizatorului curent (necesită autentificare)
```bash
curl http://localhost:8000/api/watchlist/ \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "profile": 1,
      "movie": 1,
      "movie_title": "Avatar",
      "movie_details": {...},
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### POST /api/watchlist/add_movie/
Adaugă film la watchlist (necesită autentificare)
```bash
curl -X POST http://localhost:8000/api/watchlist/add_movie/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"movie_id": 1}'
```

**Response:**
```json
{
  "id": 1,
  "profile": 1,
  "movie": 1,
  "movie_title": "Avatar",
  "movie_details": {...},
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### POST /api/watchlist/remove_movie/
Elimină film din watchlist (necesită autentificare)
```bash
curl -X POST http://localhost:8000/api/watchlist/remove_movie/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"movie_id": 1}'
```

#### DELETE /api/watchlist/{id}/
Șterge intrare din watchlist (necesită autentificare)
```bash
curl -X DELETE http://localhost:8000/api/watchlist/1/ \
  -H "Authorization: Bearer <token>"
```

---

## REST API Principles Implementation

### 1. ✅ Resource-Oriented Architecture
- Fiecare resursă (Movie, Review, User, Profile, Watchlist) are endpoint-ul propriu
- Identificatori unici (ID) pentru fiecare resursă

### 2. ✅ Standard HTTP Methods
- `GET` - Obține resurse
- `POST` - Crează resurse noi
- `PUT` - Actualizează resurse existente
- `DELETE` - Șterge resurse

### 3. ✅ HTTP Status Codes
- 2xx - Succes
- 4xx - Erori client
- 5xx - Erori server

### 4. ✅ HATEOAS (Pagination Links)
Răspunsurile includ linkuri toward alte pagini

### 5. ✅ Stateless Communication
Fiecare request conține toate informațiile necesare

### 6. ✅ Filtering, Searching, and Sorting
Suportă query parameters pentru filtrare și căutare

### 7. ✅ Content Negotiation
JSON format pentru toate răspunsurile

### 8. ✅ Authentication & Authorization
- Endpoint-urile protejate necesită autentificare
- Permisiuni granulare (ReadOnly, IsOwner, etc.)

### 9. ✅ Error Handling
Răspunsuri de eroare consistente și descriptive

### 10. ✅ Versioning Capability
API-ul poate fi versionat prin schimbarea prefixului (`/api/v1/`, `/api/v2/`)

---

## Example Usage

### Workflow complet: Creare film și recenzie

1. **Creare film** (dacă nu există)
```bash
curl -X POST http://localhost:8000/api/movies/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Avatar 2",
    "description": "Continuarea...",
    "release_date": "2024-12-20",
    "poster_url": "https://..."
  }'
```

2. **Creare recenzie pentru film**
```bash
curl -X POST http://localhost:8000/api/reviews/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "movie": 1,
    "rating": 5,
    "content": "Film fantastic!"
  }'
```

3. **Adăugare film la watchlist**
```bash
curl -X POST http://localhost:8000/api/watchlist/add_movie/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"movie_id": 1}'
```

4. **Urmărire utilizator**
```bash
curl -X POST http://localhost:8000/api/profiles/2/follow/ \
  -H "Authorization: Bearer <token>"
```
