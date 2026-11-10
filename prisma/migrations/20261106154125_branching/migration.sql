-- CreateTable
CREATE TABLE "branches" (
    "branch_id" TEXT NOT NULL,
    "parent_branch_id" TEXT,
    "fork_lamport_tick" INTEGER,
    "locked_prng_seed" BIGINT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "branches_pkey" PRIMARY KEY ("branch_id")
);

-- CreateTable
CREATE TABLE "branch_step_map" (
    "branch_id" TEXT NOT NULL,
    "lamport_tick" INTEGER NOT NULL,
    "node_id" TEXT NOT NULL,
    "is_cached_cow" BOOLEAN NOT NULL DEFAULT false,

    CONSTRAINT "branch_step_map_pkey" PRIMARY KEY ("branch_id","lamport_tick")
);

-- CreateIndex
CREATE INDEX "branches_parent_branch_id_idx" ON "branches"("parent_branch_id");

-- CreateIndex
CREATE INDEX "branch_step_map_node_id_idx" ON "branch_step_map"("node_id");

-- AddForeignKey
ALTER TABLE "branches" ADD CONSTRAINT "branches_parent_branch_id_fkey" FOREIGN KEY ("parent_branch_id") REFERENCES "branches"("branch_id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "branch_step_map" ADD CONSTRAINT "branch_step_map_branch_id_fkey" FOREIGN KEY ("branch_id") REFERENCES "branches"("branch_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "branch_step_map" ADD CONSTRAINT "branch_step_map_node_id_fkey" FOREIGN KEY ("node_id") REFERENCES "execution_nodes"("node_id") ON DELETE RESTRICT ON UPDATE CASCADE;
