/**
 * Copyright (c) 2022, RTE (http://www.rte-france.com)
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
package com.powsybl.benchmark;

import com.powsybl.loadflow.LoadFlowParameters;

/**
 * @author Geoffroy Jamgotchian <geoffroy.jamgotchian at rte-france.com>
 */
public enum ASLoadFlowParametersType implements LoadFlowParametersTypeInterface {
    BASIC(new LoadFlowParameters()
            .setVoltageInitMode(LoadFlowParameters.VoltageInitMode.PREVIOUS_VALUES)
            .setDistributedSlack(false)
            .setNoGeneratorReactiveLimits(true)
            .setPhaseShifterRegulationOn(false)
            .setTransformerVoltageControlOn(false)
            .setConnectedComponentMode(LoadFlowParameters.ConnectedComponentMode.MAIN)),
    STANDARD(new LoadFlowParameters()
            .setVoltageInitMode(LoadFlowParameters.VoltageInitMode.PREVIOUS_VALUES)
            .setDistributedSlack(true)
            .setNoGeneratorReactiveLimits(false)
            .setPhaseShifterRegulationOn(false)
            .setTransformerVoltageControlOn(false)
            .setConnectedComponentMode(LoadFlowParameters.ConnectedComponentMode.MAIN));

    private final LoadFlowParameters parameters;

    ASLoadFlowParametersType(LoadFlowParameters parameters) {
        this.parameters = parameters;
    }

    public LoadFlowParameters getParameters() {
        return parameters;
    }
}
