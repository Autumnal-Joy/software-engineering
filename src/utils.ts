// import { fetch as tauri_fetch, Body, ResponseType } from "@tauri-apps/api/http";

// const host = "http://127.0.0.1";
// const port = 8081;

// export function post<T>(
//   method: string,
//   params: Record<string, string | number>
// ) {
//   const username = localStorage.getItem("username") || "";
//   const password = localStorage.getItem("password") || "";
//   return tauri_fetch<{
//     success: boolean;
//     result: T;
//     error: {
//       code: number;
//       message: string;
//       data: string;
//     };
//   }>(`${host}:${port}/api`, {
//     method: "POST",
//     body: Body.json({
//       method,
//       params: {
//         username,
//         password,
//         ...params,
//       },
//     }),
//     responseType: ResponseType.JSON,
//   })
//     .catch(() => Promise.reject({ message: "异常" }))
//     .then(resp => {
//       const data = resp.data;
//       if (data.success) {
//         return data.result;
//       } else {
//         return Promise.reject(data.error || { message: "异常" });
//       }
//     });
// }

export function post<T>(
  method: string,
  params: Record<string, string | number>
) {
  const username = localStorage.getItem("username") || "";
  const password = localStorage.getItem("password") || "";
  return fetch("/api", {
    method: "POST",
    body: JSON.stringify({
      method,
      params: { username, password, ...params },
    }),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .catch(() => Promise.reject({ message: "异常" }))
    .then(resp => {
      return resp.json();
    })
    .catch(() => {
      return Promise.reject({ message: "异常" });
    })
    .then(data => {
      if (data.success) {
        return data.result as T;
      } else {
        return Promise.reject(data.error || { message: "异常" });
      }
    });
}
