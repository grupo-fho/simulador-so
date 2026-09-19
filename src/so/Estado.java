package so;

enum Estado {
    NOVO, PRONTO, EXECUTANDO, BLOQUEADO, FINALIZADO;

    boolean permite(Estado destino) {
        return switch (this) {
            case NOVO -> destino == PRONTO;
            case PRONTO -> destino == EXECUTANDO;
            case EXECUTANDO -> destino == PRONTO || destino == BLOQUEADO || destino == FINALIZADO;
            case BLOQUEADO -> destino == PRONTO;
            case FINALIZADO -> false;
        };
    }
}
