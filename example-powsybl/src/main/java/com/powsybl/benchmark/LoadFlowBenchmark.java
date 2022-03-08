/**
 * Copyright (c) 2022, RTE (http://www.rte-france.com)
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
package com.powsybl.benchmark;

import com.powsybl.loadflow.LoadFlow;
import com.powsybl.loadflow.LoadFlowResult;
import org.openjdk.jmh.annotations.*;

import java.util.concurrent.TimeUnit;

/**
 * @author Geoffroy Jamgotchian <geoffroy.jamgotchian at rte-france.com>
 */
@Fork(1)
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.MILLISECONDS)
public class LoadFlowBenchmark {

    // @Benchmark
    public LoadFlowResult ieee14(LoadFlowProviderState providerState, IeeeNetworkState networkState, LoadFlowParametersState parametersState) {
        return LoadFlow.find(providerState.getProvider()).run(networkState.getIeee14Network(), parametersState.getType().getParameters());
    }

    // @Benchmark
    public LoadFlowResult ieee118(LoadFlowProviderState providerState, IeeeNetworkState networkState, LoadFlowParametersState parametersState) {
        return LoadFlow.find(providerState.getProvider()).run(networkState.getIeee118Network(), parametersState.getType().getParameters());
    }

    // @Benchmark
    public LoadFlowResult ieee300(LoadFlowProviderState providerState, IeeeNetworkState networkState, LoadFlowParametersState parametersState) {
        return LoadFlow.find(providerState.getProvider()).run(networkState.getIeee300Network(), parametersState.getType().getParameters());
    }

    // @Benchmark
    // @Warmup(time = 3)
    // @Measurement(time = 5)
    public LoadFlowResult rte1888(LoadFlowProviderState providerState, Rte1888NetworkState networkState, LoadFlowParametersState parametersState) {
        return LoadFlow.find(providerState.getProvider()).run(networkState.getNetwork(), parametersState.getType().getParameters());
    }

    // @Benchmark
    // @Warmup(time = 3)
    // @Measurement(time = 5)
    public LoadFlowResult rte6515(LoadFlowProviderState providerState, Rte6515NetworkState networkState, LoadFlowParametersState parametersState) {
        return LoadFlow.find(providerState.getProvider()).run(networkState.getNetwork(), parametersState.getType().getParameters());
    }

    @Benchmark
    public LoadFlowResult case9241pegase(LoadFlowProviderState providerState, Case9241pegaseNetworkState networkState, LoadFlowParametersState parametersState) {
        return LoadFlow.find(providerState.getProvider()).run(networkState.getNetwork(), parametersState.getType().getParameters());
    }
}
