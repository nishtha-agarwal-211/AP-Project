import { z } from "zod";

const obj = z.record(z.string(), z.unknown());

export const commitSchema = z.object({
  branch_id: z.string().min(1),
  lamport_tick: z.number().int().min(0),
  agent_id: z.string().min(1),
  prompt_input: z.string(),
  llm_output: z.string(),
  token_cost: z.number().min(0),
  state_blob: obj,
  embedding: z.array(z.number()).length(1536),
  io_logs: z.array(
    z.object({
      io_seq_no: z.number().int().min(0),
      kind: z.enum(["http", "fs_read"]),
      req_payload: obj,
      res_payload: obj.nullish(),
    }),
  ),
  ast_metrics: z.object({
    net_loc_delta: z.number().int(),
    dead_ast_nodes: z.number().int().min(0),
    files_created_delta: z.number().int().min(0),
    gate_passed: z.boolean(),
  }),
});

export type CommitInput = z.infer<typeof commitSchema>;
