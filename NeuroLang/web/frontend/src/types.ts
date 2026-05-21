export type ErrorType = "syntax" | "semantic" | "io" | "unknown";

export interface CompileResponse {
  success: boolean;
  python_code?: string | null;
  ast_pretty?: string | null;
  error_type?: ErrorType | null;
  message: string;
  line?: number | null;
  column?: number | null;
  context?: string | null;
  graph_image_base64?: string | null;
  graph_message?: string | null;
}

export interface ExampleInfo {
  filename: string;
  category: "valid" | "error";
  title?: string | null;
  description?: string | null;
  tags?: string[];
}

export interface MetadataResponse {
  items: string[];
}

export type OutputTab = "compare" | "python" | "ast" | "graph" | "errors" | "log";

export interface PipelineStep {
  id: string;
  label: string;
  keyword: string;
  optional?: boolean;
}
