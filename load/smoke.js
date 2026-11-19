import http from "k6/http";
import { check } from "k6";

export const options = {
  vus: 10,
  duration: "30s",
  thresholds: {
    http_req_duration: ["p(95)<300"],
    http_req_failed: ["rate<0.01"],
  },
};

export default function () {
  const url = `${__ENV.BASE_URL}/api/books`;
  const response = http.get(url);
  check(response, { "каталог отвечает 200": (r) => r.status === 200 });
}
