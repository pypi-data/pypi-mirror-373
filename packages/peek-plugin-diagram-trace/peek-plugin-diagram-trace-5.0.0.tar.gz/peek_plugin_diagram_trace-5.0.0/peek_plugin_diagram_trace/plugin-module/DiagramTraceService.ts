import { GraphDbTraceResultTuple } from "@peek/peek_plugin_graphdb";
import { Injectable } from "@angular/core";

export interface DiagramTraceI {
    modelSetKey: string;
    traceKey: string;
    startKey: string;
    traceModel: GraphDbTraceResultTuple;
}

@Injectable()
export abstract class DiagramTraceService {
    abstract get activeTraces(): DiagramTraceI[];
}
