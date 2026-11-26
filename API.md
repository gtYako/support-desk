# API

Вход: `/api-auth/login/` или Basic Auth. Доступ только авторизованным.

- `GET /api/categories/` — категории.
- `GET /api/tickets/` — список, по 5 записей; параметры `page`, `status`, `category`, `priority`, `assignee`, `search`, `overdue=true`.
- `POST /api/tickets/` — создание: `{"category":1,"subject":"Нет доступа","description":"Не получается войти","priority":"high","response_due":"2030-12-01T12:00:00+03:00"}`.
- `GET /api/tickets/1/` — карточка.
- `PATCH /api/tickets/1/` — изменить, например `{"status":"in_progress"}`.
- `GET /api/tickets/1/events/` — история статусов.
- `GET /api/tickets/1/comments/` — комментарии; `POST` с `{"text":"Комментарий"}` добавляет новый.

Автор устанавливается сервером. Неверные данные возвращают 400, чужая запись скрыта и возвращает 404.
