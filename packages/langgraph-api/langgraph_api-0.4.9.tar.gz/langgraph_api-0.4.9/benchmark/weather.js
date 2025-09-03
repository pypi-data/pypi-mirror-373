import http from "k6/http";
import { check } from "k6";

export const options = {
  vus: 100,
  duration: "30s",
};

const ORIGIN = "http://localhost:9123";

export function setup() {
  const assistant = http.post(
    `${ORIGIN}/assistants`,
    JSON.stringify({ graph_id: "weather" }),
    { headers: { "Content-Type": "application/json" } }
  );

  check(assistant, { "assistant status is 200": (r) => r.status === 200 });

  return assistant.json();
}

export default function main(assistant) {
  const thread = http.post(`${ORIGIN}/threads`, JSON.stringify({}), {
    params: { headers: { "Content-Type": "application/json" } },
  });

  check(thread, { "thread status is 200": (r) => r.status === 200 });

  const wait = http.post(
    `${ORIGIN}/threads/${thread.json().thread_id}/runs/wait`,
    JSON.stringify({
      input: {
        messages: [{ role: "human", content: "SF", id: "initial-message" }],
      },
      assistant_id: assistant.assistant_id,
    }),
    { headers: { "Content-Type": "application/json" } }
  );

  check(wait, {
    "interrupted run status is 200": (r) => r.status === 200,
    "interrupted run has values": (r) => {
      const json = r.json();
      if (json.route !== "weather") return false;
      if (json.messages.length !== 1) return false;
      if (json.messages[0].id !== "initial-message") return false;
      if (json.messages[0].content !== "SF") return false;
      return true;
    },
  });

  const continueWait = http.post(
    `${ORIGIN}/threads/${thread.json().thread_id}/runs/wait`,
    JSON.stringify({
      input: null,
      assistant_id: assistant.assistant_id,
    }),
    { headers: { "Content-Type": "application/json" } }
  );

  check(continueWait, {
    "run status is 200": (r) => r.status === 200,
    "run has values": (r) => {
      const json = r.json();
      if (json.route !== "weather") return false;
      if (json.messages.length !== 2) return false;
      if (json.messages[0].id !== "initial-message") return false;
      if (json.messages[0].content !== "SF") return false;
      if (json.messages[1].content !== "It's sunny in San Francisco!")
        return false;
      return true;
    },
  });
}
