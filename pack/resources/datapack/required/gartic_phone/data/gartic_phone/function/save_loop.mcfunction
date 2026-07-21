scoreboard players add $prompt_index gartic_phone_counter 1

execute store result storage gartic_phone:prompt index int 1 run scoreboard players get $prompt_index gartic_phone_counter
execute store result storage gartic_phone:prompt round int 1 run scoreboard players get $round gartic_phone_counter

function gartic_phone:save_prompt with storage gartic_phone:prompt

execute unless score $prompt_index gartic_phone_counter > $count gartic_phone_counter run function gartic_phone:save_loop
