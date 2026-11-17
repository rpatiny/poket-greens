class_name Player
extends Actor
## Jogador: anda com o direcional, corre segurando "run", interage com "action".
## Um toque rápido numa direção só vira o personagem (como nos RPGs de portátil).

const TURN_GRACE := 0.09  # segundos segurando antes de começar a andar depois de virar

var _was_holding := false
var _turn_wait := 0.0
var _last_bump := Vector2i(-999, -999)
var _busy_lock := false


func _ready() -> void:
	set_texture(Game.sprite("avatar"))


func _process(delta: float) -> void:
	super(delta)
	if moving or _busy_lock or Game.is_busy():
		return

	if Game.action_pressed():
		Game.consume_action()
		_interact()
		return

	var dir := Game.held_direction()
	running = Input.is_action_pressed("run")
	if dir == Vector2i.ZERO:
		_was_holding = false
		_turn_wait = 0.0
		_last_bump = Vector2i(-999, -999)
		return

	# Sair pela borda (ex.: capacho da porta).
	var edge := map().edge_warp(cell, dir) if map() else {}
	if not edge.is_empty():
		face(dir)
		_do_warp(edge)
		return

	# Toque rápido numa direção nova (partindo do repouso) só vira o personagem.
	if dir != facing and not _was_holding:
		face(dir)
		_turn_wait = TURN_GRACE
		_was_holding = true
		return
	_was_holding = true
	if _turn_wait > 0.0:
		_turn_wait -= delta
		return

	if try_step(dir):
		_last_bump = Vector2i(-999, -999)
	else:
		_bump(cell + dir)


func _on_step_finished() -> void:
	var w := map().step_warp(cell)
	if not w.is_empty():
		_do_warp(w)


func _bump(target: Vector2i) -> void:
	if target == _last_bump:
		return
	_last_bump = target
	var e := map().entity_at(target, self)
	if e and e.get("on_bump") == true:
		_run_busy(e.interact.bind(self))


func _interact() -> void:
	var e := map().entity_at(cell + facing, self)
	if e and e.has_method("interact"):
		_run_busy(e.interact.bind(self))


func _do_warp(w: Dictionary) -> void:
	var to: Array = w["to_cell"]
	_run_busy(Game.warp.bind(w["to"], Vector2i(int(to[0]), int(to[1])), Game.DIRS.get(w.get("facing", "down"))))


## Espera uma corrotina (diálogo, troca de mapa) com os controles travados.
func _run_busy(job: Callable) -> void:
	_busy_lock = true
	await job.call()
	_busy_lock = false
