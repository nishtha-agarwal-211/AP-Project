-- CreateTable
CREATE TABLE "intercepted_io" (
    "node_id" TEXT NOT NULL,
    "io_seq_no" INTEGER NOT NULL,
    "io_type" TEXT NOT NULL,
    "req_payload" JSONB NOT NULL,
    "res_payload" JSONB,

    CONSTRAINT "intercepted_io_pkey" PRIMARY KEY ("node_id","io_seq_no")
);

-- CreateTable
CREATE TABLE "ast_vfs_guardrails" (
    "guardrail_id" TEXT NOT NULL,
    "node_id" TEXT NOT NULL,
    "files_created_delta" INTEGER NOT NULL DEFAULT 0,
    "max_allowed_files" INTEGER NOT NULL DEFAULT 0,
    "net_loc_delta" INTEGER NOT NULL DEFAULT 0,
    "dead_ast_nodes" INTEGER NOT NULL DEFAULT 0,
    "gate_passed" BOOLEAN NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ast_vfs_guardrails_pkey" PRIMARY KEY ("guardrail_id")
);

-- CreateTable
CREATE TABLE "state_diffs" (
    "diff_id" TEXT NOT NULL,
    "left_state_hash" CHAR(64) NOT NULL,
    "right_state_hash" CHAR(64) NOT NULL,
    "vector_cosine_distance" DOUBLE PRECISION NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "state_diffs_pkey" PRIMARY KEY ("diff_id")
);

-- CreateTable
CREATE TABLE "diff_patches" (
    "diff_id" TEXT NOT NULL,
    "patch_idx" INTEGER NOT NULL,
    "op" TEXT NOT NULL,
    "path" TEXT NOT NULL,
    "old_value" JSONB,
    "new_value" JSONB,

    CONSTRAINT "diff_patches_pkey" PRIMARY KEY ("diff_id","patch_idx")
);

-- CreateIndex
CREATE UNIQUE INDEX "ast_vfs_guardrails_node_id_key" ON "ast_vfs_guardrails"("node_id");

-- CreateIndex
CREATE UNIQUE INDEX "state_diffs_left_state_hash_right_state_hash_key" ON "state_diffs"("left_state_hash", "right_state_hash");

-- AddForeignKey
ALTER TABLE "intercepted_io" ADD CONSTRAINT "intercepted_io_node_id_fkey" FOREIGN KEY ("node_id") REFERENCES "execution_nodes"("node_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ast_vfs_guardrails" ADD CONSTRAINT "ast_vfs_guardrails_node_id_fkey" FOREIGN KEY ("node_id") REFERENCES "execution_nodes"("node_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "state_diffs" ADD CONSTRAINT "state_diffs_left_state_hash_fkey" FOREIGN KEY ("left_state_hash") REFERENCES "state_snapshots"("state_hash") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "state_diffs" ADD CONSTRAINT "state_diffs_right_state_hash_fkey" FOREIGN KEY ("right_state_hash") REFERENCES "state_snapshots"("state_hash") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "diff_patches" ADD CONSTRAINT "diff_patches_diff_id_fkey" FOREIGN KEY ("diff_id") REFERENCES "state_diffs"("diff_id") ON DELETE RESTRICT ON UPDATE CASCADE;
