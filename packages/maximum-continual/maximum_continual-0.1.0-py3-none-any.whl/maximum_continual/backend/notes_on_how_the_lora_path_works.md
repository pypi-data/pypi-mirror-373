Take a model with model_id, "test_model"

Initially, it should start by generating a path "test_model/initial".

In this path it should create a LoraInfoT metadata.json which contains:
{
    "step": 0,
    "model_id" : "test_model",
    "full_lora_path": None # initial has no lora. 
}

When it calls model.update() with a specified model_id, this should indicate to first:
1. Check the test_model/ folder.
2. Find the latest step.
3. Parse the metadata.json from that step.

If there are no steps, then it should parse the metadata.json from initial. 

If the full_lora_path is None, it should create a new lora model.

Then it runs a single update.

After the update, it should then generate the next lora_info_t.

The next_lora_info_t is calculated by taking the current lorainfot, adding 1 to the step count, and calculating the full_lora_path as :

"{LORA_VOL_PATH}/{model_id}/step_{next_step_count}_from_{prev_step_count}"

It should then save the lora to this path. 


What do we need for this to work?

We create a new class, ModelManager, which takes a model_id and LORA_VOL_PATH.

This ModelManager has the methods:

ModelManager.fetch_current_step(model_id) -> LoraInfoT

ModelManager.fetch_next_step(model_id) -> LoraInfoT

ModelManager.update_current_step(model_id, LoraInfoT)