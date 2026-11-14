import { prisma } from "../src/db.js";
import { commitStep } from "../src/services/commitStep.js";

const agent = await prisma.agent.create({ data: { modelName: "gpt-4o-mini" } });
const main = await prisma.branch.create({ data: { name: "main", lockedPrngSeed: 42n } });

for (let tick = 1; tick <= 12; tick++) {
  await commitStep({
    branch_id: main.branchId,
    lamport_tick: tick,
    agent_id: agent.agentId,
    prompt_input: `step ${tick} prompt`,
    llm_output: `step ${tick} output`,
    token_cost: 0.002,
    state_blob: { step: tick, memory: `after step ${tick}` },
    embedding: Array.from({ length: 1536 }, (_, j) => Math.sin(tick * 31 + j)),
    io_logs:
      tick % 3 === 0
        ? [{ io_seq_no: 0, kind: "http", req_payload: { url: "https://example.com" }, res_payload: { status: 200 } }]
        : [],
    ast_metrics: { net_loc_delta: 3, dead_ast_nodes: 0, files_created_delta: 0, gate_passed: true },
  });
}
console.log("seeded branch", main.branchId);
await prisma.$disconnect();
