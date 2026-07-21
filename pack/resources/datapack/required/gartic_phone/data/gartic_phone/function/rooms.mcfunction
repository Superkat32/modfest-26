scoreboard players operation @a[tag=gartic_phone_player] gartic_phone_tp_index = $round_room_offset gartic_phone_counter
execute as @a[tag=gartic_phone_player] run scoreboard players operation @s gartic_phone_tp_index += @s gartic_phone_offset
redstone 37 63 41 trigger
