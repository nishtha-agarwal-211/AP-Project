import { prisma } from "../src/db.js";
import { commitStep } from "../src/services/commitStep.js";

const agent = await prisma.agent.create({ data: { modelName: "t" } });
const branch = await prisma.branch.create({ data: { lockedPrngSeed: 1n } });

const mk = (tick: number) => ({
  branch_id: branch.branchId,
  lamport_tick: tick,
  agent_id: agent.agentId,
  prompt_input: "p",
  llm_output: "o",
  token_cost: 0.01,
  state_blob: { same: "state", n: 1 },
  embedding: Array(1536).fill(0.01),
  io_logs: [],
  ast_metrics: { net_loc_delta: 0, dead_ast_nodes: 0, files_created_delta: 0, gate_passed: true },
});

const a = await commitStep(mk(1));
const b = await commitStep(mk(2));

console.log("same hash:", a.state_hash === b.state_hash);
console.log(
  "snapshot rows:",
  await prisma.stateSnapshot.count({ where: { stateHash: a.state_hash } }),
); // expect 1
console.log("cumulative:", b.cumulative_cost); // expect 0.02

await prisma.$disconnect();
