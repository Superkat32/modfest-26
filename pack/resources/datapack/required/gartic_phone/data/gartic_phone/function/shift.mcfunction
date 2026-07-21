scoreboard players add @a[tag=gartic_phone_player] gartic_phone_offset 1
execute as @a[tag=gartic_phone_player] run scoreboard players operation @s gartic_phone_offset %= $count gartic_phone_counter
