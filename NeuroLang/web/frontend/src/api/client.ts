import type { CompileResponse, ExampleInfo, MetadataResponse } from "../types";

const API_BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `HTTP ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function healthCheck(): Promise<{ status: string; version: string }> {
  return request("/health");
}

export async function listExamples(): Promise<ExampleInfo[]> {
  const data = await request<{ examples: ExampleInfo[] }>("/examples");
  return data.examples;
}

export async function fetchExample(filename: string): Promise<string> {
  const data = await request<{ filename: string; content: string }>(
    `/examples/${encodeURIComponent(filename)}`,
  );
  return data.content;
}

export async function compile(
  source: string,
  visualize: boolean,
): Promise<CompileResponse> {
  return request<CompileResponse>("/compile", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source, visualize }),
  });
}

export async function fetchAst(source: string): Promise<CompileResponse> {
  return request<CompileResponse>("/ast", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source }),
  });
}

export async function fetchComponents(): Promise<string[]> {
  const data = await request<MetadataResponse>("/metadata/components");
  return data.items;
}

export async function fetchDatasets(): Promise<string[]> {
  const data = await request<MetadataResponse>("/metadata/datasets");
  return data.items;
}

export type RunStreamEvent =
  | { type: "start"; script: string }
  | { type: "log"; line: string }
  | { type: "done"; exit_code: number; success: boolean }
  | { type: "error"; message: string };

function parseSseChunk(buffer: string): { events: RunStreamEvent[]; rest: string } {
  const events: RunStreamEvent[] = [];
  const parts = buffer.split("\n\n");
  const rest = parts.pop() ?? "";
  for (const part of parts) {
    const dataLine = part.split("\n").find((l) => l.startsWith("data: "));
    if (!dataLine) continue;
    try {
      events.push(JSON.parse(dataLine.slice(6)) as RunStreamEvent);
    } catch {
      /* ignore malformed */
    }
  }
  return { events, rest };
}

export async function streamRun(
  body: { python_code?: string; source?: string; visualize?: boolean },
  handlers: {
    onEvent: (event: RunStreamEvent) => void;
    signal?: AbortSignal;
  },
): Promise<void> {
  const response = await fetch(`${API_BASE}/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify(body),
    signal: handlers.signal,
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("Brak strumienia odpowiedzi");
  }
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parsed = parseSseChunk(buffer);
    buffer = parsed.rest;
    for (const event of parsed.events) {
      handlers.onEvent(event);
    }
  }
  if (buffer.trim()) {
    const parsed = parseSseChunk(`${buffer}\n\n`);
    for (const event of parsed.events) {
      handlers.onEvent(event);
    }
  }
}

export async function uploadNl(file: File): Promise<string> {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: form,
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  const data = (await response.json()) as { content: string };
  return data.content;
}
