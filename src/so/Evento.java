package so;

record Evento(long instante, int ordemTipo, long sequencia, Runnable acao) implements Comparable<Evento> {
    @Override
    public int compareTo(Evento outro) {
        int comparacao = Long.compare(instante, outro.instante);
        if (comparacao == 0) { comparacao = Integer.compare(ordemTipo, outro.ordemTipo); }
        if (comparacao == 0) { comparacao = Long.compare(sequencia, outro.sequencia); }
        return comparacao;
    }
}
