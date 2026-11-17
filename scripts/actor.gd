class_name Actor
extends Node2D
## Personagem que anda em grade de 16×16 (jogador e NPCs).
## Folha de sprite 48×72: colunas = parado, passo A, passo B; linhas = frente, costas, perfil (olhando à esquerda).
## O lado direito é o perfil espelhado.

signal step_finished

const FRAME := Vector2i(16, 24)
const WALK_SPEED := 64.0  # px/s = 4 tiles por segundo
const RUN_SPEED := 128.0

var cell := Vector2i.ZERO
var facing := Vector2i.DOWN
var moving := false
var running := false
var solid := true

var _sprite: Sprite2D
var _from := Vector2.ZERO
var _to := Vector2.ZERO
var _t := 0.0
var _foot := false


func _init() -> void:
	_sprite = Sprite2D.new()
	_sprite.centered = false
	_sprite.region_enabled = true
	_sprite.offset = Vector2(0, Game.TILE - FRAME.y)
	add_child(_sprite)


func set_texture(tex: Texture2D) -> void:
	_sprite.texture = tex
	_update_frame()


func place(at: Vector2i, dir := Vector2i.ZERO) -> void:
	cell = at
	moving = false
	position = Vector2(at * Game.TILE)
	if dir != Vector2i.ZERO:
		facing = dir
	_update_frame()


func face(dir: Vector2i) -> void:
	facing = dir
	_update_frame()


func map() -> GameMap:
	return Game.main.current_map if Game.main else null


## Tenta andar uma célula. Retorna false se a célula estiver bloqueada (o ator só vira).
func try_step(dir: Vector2i) -> bool:
	if moving:
		return false
	face(dir)
	var target := cell + dir
	if map() == null or map().is_blocked(target, self):
		return false
	_from = position
	_to = Vector2(target * Game.TILE)
	cell = target  # reserva a célula de destino já no início
	_t = 0.0
	moving = true
	_foot = not _foot
	return true


func _process(delta: float) -> void:
	if not moving:
		return
	var speed := RUN_SPEED if running else WALK_SPEED
	_t += delta * speed / Game.TILE
	if _t >= 1.0:
		position = _to
		moving = false
		_update_frame()
		step_finished.emit()
		_on_step_finished()
		return
	position = _from.lerp(_to, _t).round()
	_update_frame()


func _on_step_finished() -> void:
	pass


func _update_frame() -> void:
	if _sprite.texture == null:
		return
	var row := 0
	match facing:
		Vector2i.UP:
			row = 1
		Vector2i.LEFT, Vector2i.RIGHT:
			row = 2
	var col := 0
	if moving and _t < 0.5:
		col = 2 if _foot else 1
	_sprite.flip_h = facing == Vector2i.RIGHT
	_sprite.region_rect = Rect2(col * FRAME.x, row * FRAME.y, FRAME.x, FRAME.y)
