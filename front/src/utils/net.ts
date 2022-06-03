import { Body, fetch as tauri_fetch, ResponseType } from "@tauri-apps/api/http";

const host = "http://127.0.0.1";
const port = 8081;

function tauriPost<T>(method: string, params: Record<string, string | number>) {
  return tauri_fetch<{
    success: boolean;
    result: T;
    error: {
      code: number;
      message: string;
      data: string;
    };
  }>(`${host}:${port}/api`, {
    method: "POST",
    body: Body.json({
      method,
      params,
    }),
    responseType: ResponseType.JSON,
  })
    .catch(() => Promise.reject({ message: "异常" }))
    .then(resp => {
      const data = resp.data;
      if (data.success) {
        return data.result;
      } else {
        return Promise.reject(data.error || { message: "异常" });
      }
    });
}

function browserPost<T>(
  method: string,
  params: Record<string, string | number>
) {
  return fetch("/api", {
    method: "POST",
    body: JSON.stringify({
      method,
      params,
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

let post = tauriPost;
if (process.env.REACT_APP_TARGET === "browser") {
  post = browserPost;
}

export { post };
