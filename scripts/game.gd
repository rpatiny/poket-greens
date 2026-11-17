extends Node
## Autoload "Game": constantes, dados compartilhados e atalhos para os serviços da cena principal.

const TILE := 16
const MAPS_DIR := "res://data/maps/"
const TILES_FILE := "res://data/tiles.json"

const DIRS := {
	"up": Vector2i.UP,
	"down": Vector2i.DOWN,
	"left": Vector2i.LEFT,
	"right": Vector2i.RIGHT,
}

## Cena principal (main.gd). Ela se registra aqui ao entrar na árvore.
var main: Node = null

var _tile_db: Dictionary = {}
var _tile_set: TileSet = null
var _source_ids: Dictionary = {}
var _action_consumed_frame := -1


func _ready() -> void:
	if not OS.get_locale().begins_with("en") and not OS.get_locale().begins_with("es"):
		TranslationServer.set_locale("pt_BR")


# --- Entrada -----------------------------------------------------------------

## true no quadro em que o botão de ação foi apertado, se ninguém o usou ainda.
## Evita que o mesmo aperto feche um diálogo e abra outro.
func action_pressed() -> bool:
	return Input.is_action_just_pressed("action") and _action_consumed_frame != Engine.get_process_frames()


func consume_action() -> void:
	_action_consumed_frame = Engine.get_process_frames()


var _held: Array[Vector2i] = []


func _process(_delta: float) -> void:
	for name in DIRS:
		var dir: Vector2i = DIRS[name]
		var down := Input.is_action_pressed("move_" + name)
		if down and not _held.has(dir):
			_held.append(dir)
		elif not down and _held.has(dir):
			_held.erase(dir)


## Direção segurada no momento. Com duas teclas apertadas, vale a mais recente.
func held_direction() -> Vector2i:
	return _held.back() if not _held.is_empty() else Vector2i.ZERO


func dir_name(dir: Vector2i) -> String:
	for name in DIRS:
		if DIRS[name] == dir:
			return name
	return "down"


# --- Dados -------------------------------------------------------------------

func load_json(path: String) -> Variant:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		push_error("Não foi possível abrir %s" % path)
		return null
	var data: Variant = JSON.parse_string(file.get_as_text())
	if data == null:
		push_error("JSON inválido em %s" % path)
	return data


func map_data(map_id: String) -> Dictionary:
	var data: Variant = load_json(MAPS_DIR + map_id + ".json")
	return data if data is Dictionary else {}


func tile_db() -> Dictionary:
	if _tile_db.is_empty():
		_tile_db = load_json(TILES_FILE)
	return _tile_db


## TileSet montado a partir de data/tiles.json (um atlas por textura).
func tile_set() -> TileSet:
	if _tile_set != null:
		return _tile_set
	_tile_set = TileSet.new()
	_tile_set.tile_size = Vector2i(TILE, TILE)
	var textures: Dictionary = tile_db()["textures"]
	for tex_name in textures:
		var tex: Texture2D = load(textures[tex_name])
		var src := TileSetAtlasSource.new()
		src.texture = tex
		src.texture_region_size = Vector2i(TILE, TILE)
		for y in tex.get_height() / TILE:
			for x in tex.get_width() / TILE:
				src.create_tile(Vector2i(x, y))
		_source_ids[tex_name] = _tile_set.add_source(src)
	return _tile_set


func source_id(tex_name: String) -> int:
	tile_set()
	return _source_ids.get(tex_name, -1)


func sprite(name: String) -> Texture2D:
	return load("res://assets/sprites/%s.png" % name)


# --- Serviços da cena principal ----------------------------------------------

func is_busy() -> bool:
	return main != null and main.is_busy()


## Mostra uma sequência de falas (chaves de tradução) e espera o jogador terminar de ler.
func say(lines: Array, speaker := "") -> void:
	if main:
		await main.say(lines, speaker)


func warp(map_id: String, cell: Vector2i, facing: Vector2i) -> void:
	if main:
		await main.change_map(map_id, cell, facing)
