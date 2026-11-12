import { Prisma } from "../../generated/prisma/client.js";
import { prisma } from "../db.js";
import { canonicalJson, sha256Hex } from "../canonical.js";
import type { CommitInput } from "../schemas/commit.js";

const asJson = (v: unknown) => v as Prisma.InputJsonValue;

export async function commitStep(b: CommitInput) {
  const stateHash = sha256Hex(b.state_blob);
  const blobJson = canonicalJson(b.state_blob);
  const vector = `[${b.embedding.join(",")}]`; // pgvector text literal

  return prisma.$transaction(async (tx) => {
    // 1. Snapshot: raw SQL because of the vector column. Same state => no-op.
    await tx.$executeRaw`
      INSERT INTO "state_snapshots" ("state_hash", "memory_blob_json", "embedding_vector")
      VALUES (${stateHash}, ${blobJson}::jsonb, ${vector}::vector)
      ON CONFLICT ("state_hash") DO NOTHING`;

    // 2. Execution node
    const node = await tx.executionNode.create({
      data: {
        agentId: b.agent_id,
        stateHash,
        lamportTick: b.lamport_tick,
        promptInput: b.prompt_input,
        llmOutput: b.llm_output,
        tokenCost: b.token_cost,
      },
    });

    // 3. Branch -> step mapping
    await tx.branchStepMap.create({
      data: {
        branchId: b.branch_id,
        lamportTick: b.lamport_tick,
        nodeId: node.nodeId,
        isCachedCow: false,
      },
    });

    // 4. Intercepted I/O (note: Python `kind` -> DB `io_type`)
    if (b.io_logs.length > 0) {
      await tx.interceptedIo.createMany({
        data: b.io_logs.map((l) => ({
          nodeId: node.nodeId,
          ioSeqNo: l.io_seq_no,
          ioType: l.kind,
          reqPayload: asJson(l.req_payload),
          resPayload: l.res_payload == null ? Prisma.DbNull : asJson(l.res_payload),
        })),
      });
    }

    // 5. Guardrail row
    await tx.astVfsGuardrail.create({
      data: {
        nodeId: node.nodeId,
        filesCreatedDelta: b.ast_metrics.files_created_delta,
        netLocDelta: b.ast_metrics.net_loc_delta,
        deadAstNodes: b.ast_metrics.dead_ast_nodes,
        gatePassed: b.ast_metrics.gate_passed,
      },
    });

    // 6. cumulative_cost = sum(token_cost) over this branch's steps
    const agg = await tx.executionNode.aggregate({
      _sum: { tokenCost: true },
      where: { branchSteps: { some: { branchId: b.branch_id } } },
    });

    return {
      node_id: node.nodeId,
      state_hash: stateHash,
      gate_passed: b.ast_metrics.gate_passed,
      cumulative_cost: agg._sum.tokenCost?.toNumber() ?? 0,
    };
  });
}
