import argparse
import json
from pathlib import Path

import common

# Creates pack data based on information from the master `music_tracker_data.json` file
# The master file's content is to be copy-pasted from the Google Sheets Music Tracker's "Scripts" sheet,
# found within the magenta "Pack JSON Data" table
def main(gen_translations, gen_sounds, gen_item):
	repo_root = common.get_repo_root()
	music_pack_folder = get_music_pack_folder()

	master_tracker_data_path = repo_root / "scripts/music_tracker_data.json"
	jukebox_folder = music_pack_folder / "data/modfest/jukebox_song/"
	jukebox_stereo_folder = jukebox_folder / "stereo"

	print(f"Running music data script!")
	if not gen_translations: print("Skipping translations!")
	if not gen_sounds: print("Skipping sounds.json!")
	if not gen_item: print("Skipping item and item models!")
	print(f"Master jukebox data file: {master_tracker_data_path}")
	print(f"Pack jukebox folder: {jukebox_folder}")
	print(f"Pack jukebox stereo folder: {jukebox_stereo_folder}\n")

	lang_translations_dict = {} # Contain all song translations to write all at once
	sounds_entries_dict = {} # Contain all modfest/sounds.json entries to write all at once
	mc_sounds_entries_dict = {} # Contain all minecraft/sounds.json to write all at once
	song_count = 0

	# Loop through each song entry from the master file
	print(f"Generating Jukebox {"and Item" if gen_item else ""} data...")
	with open(master_tracker_data_path, "r") as master_data_file:
		for song_data in json.load(master_data_file):
			# Read info from the master file
			song_title = song_data["title"]
			song_id = song_data["id"]
			song_lore = song_data["lore"]
			song_length_seconds = song_data["length"]
			is_menu_music = song_data["is_menu"] if "is_menu" in song_data else False
			is_credits_music = song_data["is_credits"] if "is_credits" in song_data else False

			# Create or update jukebox data jsons
			create_song_jukebox_data_file(song_id, song_length_seconds, False)
			create_song_jukebox_data_file(song_id, song_length_seconds, True)

			# Get language json data to append to the language file
			if gen_translations: append_song_translations(lang_translations_dict, song_id, song_title, song_lore)
			# Get sound json data to append to the sounds.json file
			if gen_sounds:
				append_song_sounds(sounds_entries_dict, song_id)
				if is_menu_music: append_replace_song_sounds(mc_sounds_entries_dict, "music.menu", song_id)
				if is_credits_music:append_replace_song_sounds(mc_sounds_entries_dict, "music.credits", song_id)

			# Create or update item model jsons
			if gen_item: create_item_and_model(song_id)

			# Increase song count for an easy-to-glance-at confirmation of the changes at end of script
			song_count += 1
	print(f"Jukebox {"and Item" if gen_item else ""} data done!\n")

	if gen_sounds:
		sounds_path = music_pack_folder / "assets/modfest/sounds.json"
		mc_sounds_path = music_pack_folder / "assets/minecraft/sounds.json"

		print("Generating sounds...")
		# Get initial sounds data from modfest/sounds.json if existing
		sounds_data =  json.loads(common.read_file(sounds_path)) if sounds_path.exists() else {}
		for sound in sounds_entries_dict:
			sound_already_existed = sound in sounds_data
			sounds_data[sound] = sounds_entries_dict[sound] # Append or update key with value
			print(f"{"Rewrote" if sound_already_existed else "Appended"} {sound}")
		with open(sounds_path, "w", encoding="utf8") as sounds_file:
			json.dump(sounds_data, sounds_file, indent="\t")

		# Get initial sounds data from minecraft/sounds.json if existing
		mc_sounds_data = json.loads(common.read_file(mc_sounds_path)) if mc_sounds_path.exists() else {}
		for mc_sound in mc_sounds_entries_dict:
			mc_sound_already_existed = mc_sound in mc_sounds_data
			mc_sounds_data[mc_sound] = mc_sounds_entries_dict[mc_sound]
			print(f"{"Rewrote" if mc_sound_already_existed else "Appended"} {mc_sound} to minecraft/sounds.json")
		with open(mc_sounds_path, "w", encoding="utf8") as mc_sounds_file:
			json.dump(mc_sounds_data, mc_sounds_file, indent="\t")
		print("Sounds done!\n")

	if gen_translations:
		lang_folder = music_pack_folder / "assets/modfest/lang/"
		en_us_lang_path = lang_folder / "en_us.json"

		print("Generating translations...")
		# Get initial lang data if the en_us.json file exists
		lang_data = json.loads(common.read_file(en_us_lang_path)) if en_us_lang_path.exists() else {}
		for lang in lang_translations_dict:
			lang_already_existed = lang in lang_data
			lang_data[lang] = lang_translations_dict[lang] # Append or update key with value
			print(f"{"Rewrote" if lang_already_existed else "Appended"} {lang}")
		with open(en_us_lang_path, "w", encoding="utf8") as lang_file:
			# Write everything to the file
			json.dump(lang_data, lang_file, indent="\t")
		print("Translations done!\n")

	print(f"Done! Song count: {song_count}")

def create_song_jukebox_data_file(song_id, song_length_seconds, is_stereo):
	jukebox_folder = get_music_pack_folder() / "data/modfest/jukebox_song/"
	jukebox_stereo_folder = jukebox_folder / "stereo"

	song_file_path = f"{jukebox_stereo_folder if is_stereo else jukebox_folder}/{song_id}.json"
	song_file_already_exists = Path(song_file_path).exists()

	stereo_key = "stereo." if is_stereo else ""
	translation_key = f"modfest.music.{stereo_key}{song_id}"
	sound_id = f"modfest:music.{stereo_key}{song_id}"
	song_data = {
		"comparator_output": 1,
		"description": {
			"translate": translation_key
		},
		"length_in_seconds": float(song_length_seconds),
		"sound_event": {
			"sound_id": sound_id
		}
	}

	with open(song_file_path, "w", encoding="utf8") as song_file:
		json.dump(song_data, song_file, indent="\t")
		# "Created" means a new file was created, then written too
		# "Rewrote" means any amount of text was updated, or identical looking text was written to the file
		print(f"{"Rewrote" if song_file_already_exists else "Created"} jukebox {"stereo " if is_stereo else ""}data: {song_id}")

def append_song_translations(lang_translations, song_id, song_title, song_lore):
	song_lang_key = f"modfest.music.{song_id}"
	song_stereo_lang_key = f"modfest.music.stereo.{song_id}"
	lore_key = f"lore.modfest.music.{song_id}"

	lang_translations[song_lang_key] = f"{song_title} (Jukebox)"
	lang_translations[song_stereo_lang_key] = song_title
	lang_translations[lore_key] = song_lore

def append_song_sounds(sounds_entries_dict, song_id):
	song_sound_key = f"music.{song_id}"
	song_sound_value = {
		"sounds": [
			{
				"name": f"modfest:music/{song_id}",
				"stream": True
			}
		]
	}
	song_stereo_sound_key = f"music.stereo.{song_id}"
	song_stereo_sound_value = {
		"sounds": [
			{
				"name": f"modfest:music/stereo/{song_id}",
				"stream": True
			}
		]
	}
	sounds_entries_dict[song_sound_key] = song_sound_value
	sounds_entries_dict[song_stereo_sound_key] = song_stereo_sound_value

def append_replace_song_sounds(minecraft_sounds_entries_dict, key_to_replace, song_id):
	minecraft_sounds_entries_dict[key_to_replace] = {
		"replace": True,
		"sounds": [
			{
				"name": f"modfest:music/stereo/{song_id}",
				"stream": True
			}
		]
	}

def create_item_and_model(song_id):
	item_folder = get_music_pack_folder() / "assets/modfest/items/music/"
	song_item_path = f"{item_folder}/{song_id}.json"
	item_already_existed = Path(song_item_path).exists()
	item_data = {
		"model": {
			"type": "minecraft:model",
			"model": f"modfest:item/music/{song_id}"
		}
	}
	with open(song_item_path, "w", encoding="utf8") as item_file:
		json.dump(item_data, item_file, indent="\t")
		print(f"{"Rewrote" if item_already_existed else "Created" } item data: {song_id}")

	item_model_folder = get_music_pack_folder() / "assets/modfest/models/item/music/"
	song_item_model_path = f"{item_model_folder}/{song_id}.json"
	item_model_already_existed = Path(song_item_model_path).exists()
	item_model_data = {
		"parent": "minecraft:item/generated",
		"textures": {
			"layer0": f"modfest:item/music/{song_id}"
		}
	}
	with open(song_item_model_path, "w", encoding="utf8") as item_model_file:
		json.dump(item_model_data, item_model_file, indent="\t")
		print(f"{"Rewrote" if item_model_already_existed else "Created" } item model data: {song_id}")

def get_music_pack_folder():
	repo_root = common.get_repo_root()
	return repo_root / "pack/resources/common/required/mf_music/"

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description="Script for generating jukebox data (stereo and mono), translation keys, sounds.json keys, and item data & models for songs & music discs."
	)
	parser.add_argument("-nt", "--no-translations", dest="translations", action="store_false")
	parser.add_argument("-ns", "--no-sounds", dest="sounds", action="store_false")
	parser.add_argument("-ni", "--no-items", dest="items", action="store_false")

	args = parser.parse_args()
	generate_translations = args.translations
	generate_sounds = args.sounds
	generate_items = args.items
	main(generate_translations, generate_sounds, generate_items)
